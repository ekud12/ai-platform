#!/usr/bin/env node
/**
 * Unified BeforeTool hook - handles all pre-tool checks in one process.
 *
 * Replaces: panic-check.ps1, branch-guard.ps1, command-guard.ps1,
 *           secret-scanner.ps1, linter-check.ps1
 *
 * Performance: ~30-50ms vs ~2500ms (5 PowerShell processes)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const WORKSPACE = process.env.GEMINI_PROJECT_DIR || process.cwd();
const HOOKS_DIR = __dirname;
const PROTECTED_BRANCHES = ['main', 'master', 'production', 'release', 'develop'];

// Secret patterns (compiled once)
const SECRET_PATTERNS = [
    /eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*/i,  // JWT
    /sk-[a-zA-Z0-9]{20,}/,                                          // OpenAI-style keys
    /AIza[0-9A-Za-z-_]{35}/,                                        // Google API Key
    /ghp_[a-zA-Z0-9]{36}/,                                          // GitHub PAT
    /AKIA[0-9A-Z]{16}/,                                             // AWS Access Key
];

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

// 2. BRANCH GUARD - quick git check
function checkBranch() {
    try {
        const branch = execSync('git rev-parse --abbrev-ref HEAD', {
            encoding: 'utf8',
            timeout: 1000,
            stdio: ['pipe', 'pipe', 'pipe']
        }).trim();

        if (PROTECTED_BRANCHES.includes(branch)) {
            result('block', `Protected branch '${branch}'. Create a feature branch first.`);
        }
    } catch {
        // Not a git repo or git not available - allow
    }
}

// 3. COMMAND GUARD - check shell commands
function checkCommand(input) {
    if (!input) return;

    const shellTools = ['shell', 'bash', 'execute_command', 'run_terminal_command', 'run_command', 'terminal', 'cmd'];
    if (!shellTools.includes(input.tool)) return;

    const command = input.parameters?.command || input.parameters?.cmd || input.parameters?.script || '';
    if (!command) return;

    // Load blocked patterns
    const configPath = path.join(HOOKS_DIR, 'blocked-commands.json');
    if (!fs.existsSync(configPath)) return;

    try {
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

        // Check blocked patterns
        for (const rule of config.blocked_patterns || []) {
            if (new RegExp(rule.pattern, 'i').test(command)) {
                result('block', rule.reason || `Blocked: ${rule.pattern}`);
            }
        }

        // Check allowed patterns
        for (const rule of config.allowed_patterns || []) {
            if (new RegExp(rule.pattern, 'i').test(command)) {
                return; // Explicitly allowed
            }
        }

        // Default action
        if (config.default_action === 'block') {
            result('block', 'Command not in allowlist');
        }
    } catch {}
}

// 4. SECRET SCANNER - only for file write operations
function checkSecrets(input) {
    if (!input) return;

    const writeTools = ['write_file', 'create_file', 'edit_file', 'append_file'];
    if (!writeTools.includes(input.tool)) return;

    const content = input.parameters?.content || input.parameters?.text || '';
    if (!content) return;

    for (const pattern of SECRET_PATTERNS) {
        if (pattern.test(content)) {
            result('block', 'Potential secret detected in file content');
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
