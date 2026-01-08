#!/usr/bin/env node
/**
 * Unified BeforeAgent hook - handles all pre-agent checks in one process.
 *
 * Replaces: compile-rules.ps1, constitution-load.ps1, os-check.ps1
 *
 * Performance: ~50-100ms vs ~1500ms (3 PowerShell processes)
 *
 * Note: architecture-sync (generate-map.js) runs separately as it's already Node.js
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');

// Configuration (using smart path resolver)
const paths = require('../lib/paths');
const WORKSPACE = paths.workspace;
const GEMINI_DIR = paths.gemini;
const RULES_DIR = paths.files.rules;
const COMPILED_DIR = paths.files.compiledRules;

// Result helper
function output(decision, reason, additionalContext = null) {
    const result = { decision, reason };
    if (additionalContext) result.additionalContext = additionalContext;
    console.log(JSON.stringify(result));
}

// 1. PANIC CHECK - same as before-tool but we check here too
function checkPanic() {
    const panicFile = path.join(WORKSPACE, '.panic');
    if (fs.existsSync(panicFile)) {
        output('block', 'PANIC MODE: .panic file detected');
        process.exit(1);
    }
}

// 2. COMPILE RULES CHECK - check if any .rules.md is newer than .rules.json
function checkRulesStale() {
    if (!fs.existsSync(RULES_DIR) || !fs.existsSync(COMPILED_DIR)) {
        return { stale: false, count: 0 };
    }

    let staleCount = 0;
    const mdFiles = [];

    // Recursively find all .rules.md files
    function findMdFiles(dir) {
        try {
            const entries = fs.readdirSync(dir, { withFileTypes: true });
            for (const entry of entries) {
                const fullPath = path.join(dir, entry.name);
                if (entry.isDirectory() && entry.name !== 'compiled') {
                    findMdFiles(fullPath);
                } else if (entry.name.endsWith('.rules.md')) {
                    mdFiles.push(fullPath);
                }
            }
        } catch {}
    }

    findMdFiles(RULES_DIR);

    // Check each md file against its compiled json
    for (const mdFile of mdFiles) {
        const relativePath = path.relative(RULES_DIR, mdFile);
        const parts = relativePath.split(path.sep);
        const domain = parts[0];
        const name = path.basename(mdFile, '.rules.md');
        const jsonFile = path.join(COMPILED_DIR, `${domain}-${name}.rules.json`);

        if (!fs.existsSync(jsonFile)) {
            staleCount++;
            continue;
        }

        const mdStat = fs.statSync(mdFile);
        const jsonStat = fs.statSync(jsonFile);

        if (mdStat.mtimeMs > jsonStat.mtimeMs) {
            staleCount++;
        }
    }

    return { stale: staleCount > 0, count: staleCount };
}

// Compile rules if stale
function compileRulesIfNeeded() {
    const { stale, count } = checkRulesStale();

    if (!stale) {
        return true;
    }

    console.error(`[compile-rules] ${count} stale rule(s) detected, compiling...`);

    const compileScript = paths.resolveGemini('tools/rules/compile-rules.py');
    if (!fs.existsSync(compileScript)) {
        console.error('[compile-rules] compile-rules.py not found');
        return true; // Don't block
    }

    try {
        execSync(`python "${compileScript}" --quiet`, {
            encoding: 'utf8',
            timeout: 10000,
            stdio: ['pipe', 'pipe', 'pipe']
        });
        console.error('[compile-rules] Rules compiled successfully');
        return true;
    } catch (err) {
        console.error('[compile-rules] Warning: compilation failed');
        return true; // Don't block agent execution
    }
}

// 3. CONSTITUTION LOAD - just return the context
function getConstitutionalContext() {
    return 'Constitutional constraints active: CONST-001 Human supremacy, CONST-002 Panic halt, CONST-003 Single ownership, CONST-004 No code execution, CONST-005 Explicit prohibition.';
}

// 4. OS CHECK - verify .gemini is in sync (skip network fetch for speed)
function checkOsSync() {
    try {
        // Just check if we're in a git repo with .gemini tracked
        execSync('git rev-parse --is-inside-work-tree', {
            encoding: 'utf8',
            timeout: 1000,
            stdio: ['pipe', 'pipe', 'pipe']
        });

        // Check local status only (no network)
        const status = execSync('git status --porcelain .gemini', {
            encoding: 'utf8',
            timeout: 1000,
            stdio: ['pipe', 'pipe', 'pipe']
        }).trim();

        if (status) {
            console.error('[os-check] Warning: .gemini has uncommitted changes');
        }
    } catch {
        // Not a git repo or .gemini not tracked - that's fine
    }
}

// Main execution
async function main() {
    const startTime = Date.now();

    // Run all checks
    checkPanic();
    compileRulesIfNeeded();
    checkOsSync();

    const elapsed = Date.now() - startTime;
    const context = getConstitutionalContext();

    output('allow', `Agent ready (${elapsed}ms)`, context);
}

main();
