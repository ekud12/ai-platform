#!/usr/bin/env node
/**
 * Unified BeforeTool hook - handles all pre-tool checks in one process.
 *
 * Replaces: panic-check.ps1, branch-guard.ps1, command-guard.ps1,
 *           secret-scanner.ps1, linter-check.ps1
 *
 * Configuration files (single source of truth):
 *   - blocked-commands.json: Command allow/block patterns
 *   - protected-branches.json: Git branch protection rules
 *   - secret-patterns.json: Secret detection patterns
 *
 * Performance: ~30-50ms vs ~2500ms (5 PowerShell processes)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const WORKSPACE = process.env.GEMINI_PROJECT_DIR || process.cwd();
const HOOKS_DIR = __dirname;

// Configuration file paths
const CONFIG_FILES = {
    commands: path.join(HOOKS_DIR, 'blocked-commands.json'),
    branches: path.join(HOOKS_DIR, 'protected-branches.json'),
    secrets: path.join(HOOKS_DIR, 'secret-patterns.json')
};

// Cache for loaded configurations (loaded once per execution)
let configCache = {};

/**
 * Load a JSON configuration file with caching
 */
function loadConfig(key) {
    if (configCache[key]) return configCache[key];

    const filePath = CONFIG_FILES[key];
    if (!filePath || !fs.existsSync(filePath)) return null;

    try {
        configCache[key] = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        return configCache[key];
    } catch (err) {
        console.error(`Warning: Failed to load ${key} config: ${err.message}`);
        return null;
    }
}

/**
 * Get protected branches from configuration file
 */
function getProtectedBranches() {
    const config = loadConfig('branches');
    if (!config || !config.protected_branches) {
        // Fallback defaults if config missing
        return ['main', 'master', 'production', 'release', 'develop'];
    }
    return config.protected_branches.map(b => b.name);
}

/**
 * Get secret patterns from configuration file
 */
function getSecretPatterns() {
    const config = loadConfig('secrets');
    if (!config || !config.secret_patterns) {
        // Fallback defaults if config missing
        return [
            { pattern: 'eyJ[A-Za-z0-9-_=]+\\.[A-Za-z0-9-_=]+\\.?[A-Za-z0-9-_.+/=]*', flags: 'i' },
            { pattern: 'sk-[a-zA-Z0-9]{20,}', flags: '' },
            { pattern: 'AIza[0-9A-Za-z-_]{35}', flags: '' },
            { pattern: 'ghp_[a-zA-Z0-9]{36}', flags: '' },
            { pattern: 'AKIA[0-9A-Z]{16}', flags: '' }
        ];
    }
    return config.secret_patterns;
}

/**
 * Compile a pattern from config into a RegExp
 */
function compilePattern(patternConfig) {
    if (typeof patternConfig === 'string') {
        return new RegExp(patternConfig, 'i');
    }
    const flags = patternConfig.flags || '';
    return new RegExp(patternConfig.pattern, flags);
}

// Result helper
function result(decision, reason) {
    console.log(JSON.stringify({ decision, reason }));
    process.exit(decision === 'block' ? 1 : 0);
}

// Parse input from stdin or args
function getInput() {
    try {
        // Try reading from stdin (non-blocking check)
        const input = fs.readFileSync(0, 'utf8').trim();
        if (input) return JSON.parse(input);
    } catch {}
    return null;
}

// 1. PANIC CHECK - instant file existence
function checkPanic() {
    const panicFile = path.join(WORKSPACE, '.panic');
    if (fs.existsSync(panicFile)) {
        result('block', 'PANIC MODE: .panic file detected. All operations halted.');
    }
}

// 2. BRANCH GUARD - check against protected-branches.json
function checkBranch() {
    const config = loadConfig('branches');

    // Skip if branch protection is disabled
    if (config?.settings?.block_on_protected === false) {
        return;
    }

    try {
        const branch = execSync('git rev-parse --abbrev-ref HEAD', {
            encoding: 'utf8',
            timeout: 1000,
            stdio: ['pipe', 'pipe', 'pipe']
        }).trim();

        const protectedBranches = getProtectedBranches();

        if (protectedBranches.includes(branch)) {
            // Find the specific branch config for a better error message
            const branchConfig = config?.protected_branches?.find(b => b.name === branch);
            const reason = branchConfig?.reason || 'Create a feature branch first.';
            result('block', `Protected branch '${branch}'. ${reason}`);
        }
    } catch {
        // Not a git repo or git not available - allow
    }
}

// 3. COMMAND GUARD - check against blocked-commands.json
function checkCommand(input) {
    if (!input) return;

    const shellTools = ['shell', 'bash', 'execute_command', 'run_terminal_command', 'run_command', 'terminal', 'cmd'];
    if (!shellTools.includes(input.tool)) return;

    const command = input.parameters?.command || input.parameters?.cmd || input.parameters?.script || '';
    if (!command) return;

    const config = loadConfig('commands');
    if (!config) return;

    // Check blocked patterns first (higher priority)
    for (const rule of config.blocked_patterns || []) {
        try {
            if (new RegExp(rule.pattern, 'i').test(command)) {
                result('block', rule.reason || `Blocked: ${rule.pattern}`);
            }
        } catch (err) {
            console.error(`Warning: Invalid blocked pattern: ${rule.pattern}`);
        }
    }

    // Check allowed patterns
    for (const rule of config.allowed_patterns || []) {
        try {
            if (new RegExp(rule.pattern, 'i').test(command)) {
                return; // Explicitly allowed
            }
        } catch (err) {
            console.error(`Warning: Invalid allowed pattern: ${rule.pattern}`);
        }
    }

    // Default action
    if (config.default_action === 'block') {
        result('block', 'Command not in allowlist');
    }
}

// 4. SECRET SCANNER - check against secret-patterns.json
function checkSecrets(input) {
    if (!input) return;

    const config = loadConfig('secrets');

    // Skip if secret scanning is disabled
    if (config?.settings?.scan_file_writes === false) {
        return;
    }

    const writeTools = ['write_file', 'create_file', 'edit_file', 'append_file'];
    if (!writeTools.includes(input.tool)) return;

    const content = input.parameters?.content || input.parameters?.text || '';
    if (!content) return;

    // Check exclusions first
    const filePath = input.parameters?.path || input.parameters?.file_path || '';
    if (filePath && config?.exclusions) {
        for (const exclusion of config.exclusions) {
            try {
                if (new RegExp(exclusion.pattern, 'i').test(filePath)) {
                    return; // File is excluded from scanning
                }
            } catch {}
        }
    }

    // Check for secrets
    const secretPatterns = getSecretPatterns();
    for (const patternConfig of secretPatterns) {
        try {
            const pattern = compilePattern(patternConfig);

            // If pattern requires context, check for context keywords
            if (patternConfig.requires_context) {
                const hasContext = patternConfig.requires_context.some(
                    ctx => content.toLowerCase().includes(ctx.toLowerCase())
                );
                if (!hasContext) continue;
            }

            if (pattern.test(content)) {
                const description = patternConfig.description || 'secret';
                result('block', `Potential ${description} detected in file content`);
            }
        } catch (err) {
            console.error(`Warning: Invalid secret pattern: ${patternConfig.pattern || patternConfig}`);
        }
    }
}

// 5. Skip linter for now - it's inherently slow and should only run on commit
// Could add a lightweight check here if needed

// Main execution
async function main() {
    const startTime = Date.now();
    const input = getInput();

    // Run all checks (order matters - fastest/most critical first)
    checkPanic();
    checkBranch();
    checkCommand(input);
    checkSecrets(input);

    // All checks passed
    const elapsed = Date.now() - startTime;
    result('allow', `All checks passed (${elapsed}ms)`);
}

main();
