#!/usr/bin/env node
/**
 * BeforeAgent hook - handles pre-agent checks.
 *
 * Checks: panic file, stale rules, git sync
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const paths = require('../lib/paths');
const WORKSPACE = paths.workspace;
const GEMINI_DIR = paths.gemini;
const RULES_DIR = paths.files.rules;
const COMPILED_DIR = paths.files.compiledRules;

function output(decision, reason, additionalContext = null) {
    const result = { decision, reason };
    if (additionalContext) result.additionalContext = additionalContext;
    console.log(JSON.stringify(result));
}

// Sync .geminiignore from .gemini folder to workspace root
function syncGeminiIgnore() {
    const sourceFile = path.join(GEMINI_DIR, '.geminiignore');
    const targetFile = path.join(WORKSPACE, '.geminiignore');

    if (!fs.existsSync(sourceFile)) return;

    try {
        if (fs.existsSync(targetFile)) {
            const sourceStat = fs.statSync(sourceFile);
            const targetStat = fs.statSync(targetFile);
            if (targetStat.mtimeMs >= sourceStat.mtimeMs) return;
        }
        fs.copyFileSync(sourceFile, targetFile);
        console.error('[sync] Updated .geminiignore in workspace root');
    } catch {
        console.error('[sync] Warning: could not sync .geminiignore');
    }
}

// PANIC CHECK
function checkPanic() {
    const panicFile = path.join(WORKSPACE, '.panic');
    if (fs.existsSync(panicFile)) {
        output('block', 'PANIC MODE: .panic file detected');
        process.exit(1);
    }
}

// Check if rules need recompilation
function checkRulesStale() {
    if (!fs.existsSync(RULES_DIR) || !fs.existsSync(COMPILED_DIR)) {
        return { stale: false, count: 0 };
    }

    let staleCount = 0;
    const mdFiles = [];

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

function compileRulesIfNeeded() {
    const { stale, count } = checkRulesStale();
    if (!stale) return true;

    console.error(`[compile-rules] ${count} stale rule(s) detected, compiling...`);

    const compileScript = paths.resolveGemini('lib/compile-rules.py');
    if (!fs.existsSync(compileScript)) {
        console.error('[compile-rules] compile-rules.py not found');
        return true;
    }

    try {
        execSync(`python "${compileScript}" --quiet`, {
            encoding: 'utf8',
            timeout: 10000,
            stdio: ['pipe', 'pipe', 'pipe']
        });
        console.error('[compile-rules] Rules compiled successfully');
    } catch {
        console.error('[compile-rules] Warning: compilation failed');
    }
    return true;
}

function checkOsSync() {
    try {
        execSync('git rev-parse --is-inside-work-tree', {
            encoding: 'utf8',
            timeout: 1000,
            stdio: ['pipe', 'pipe', 'pipe']
        });

        const status = execSync('git status --porcelain .gemini', {
            encoding: 'utf8',
            timeout: 1000,
            stdio: ['pipe', 'pipe', 'pipe']
        }).trim();

        if (status) {
            console.error('[os-check] Warning: .gemini has uncommitted changes');
        }
    } catch {
        // Not a git repo - that's fine
    }
}

async function main() {
    const startTime = Date.now();

    syncGeminiIgnore();
    checkPanic();
    compileRulesIfNeeded();
    checkOsSync();

    const elapsed = Date.now() - startTime;
    output('allow', `Agent ready (${elapsed}ms)`);
}

main();
