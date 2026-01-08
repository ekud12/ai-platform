#!/usr/bin/env node
/**
 * Unified AfterAgent hook - handles all post-agent tasks.
 *
 * Runs after every agent completes (wiggum or standalone).
 * Updates project memory: architecture map, lessons learned.
 *
 * Performance: ~100-200ms
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration (using smart path resolver)
const paths = require('../lib/paths');
const WORKSPACE = paths.workspace;
const GEMINI_DIR = paths.gemini;
const GEMMEM_DIR = paths.gemmem;

// Result helper
function output(decision, reason) {
    console.log(JSON.stringify({ decision, reason }));
}

// 1. Update Architecture Map
function updateArchitectureMap() {
    const mapScript = paths.resolveGemini('tools/docs/generate-map.js');

    if (!fs.existsSync(mapScript)) {
        console.error('[memory] generate-map.js not found, skipping');
        return;
    }

    try {
        execSync(`node "${mapScript}"`, {
            encoding: 'utf8',
            timeout: 5000,
            stdio: ['pipe', 'pipe', 'pipe'],
            cwd: WORKSPACE
        });
    } catch (err) {
        console.error('[memory] Warning: architecture map update failed');
    }
}

// 2. Update ARCHITECTURE.md timestamp
function touchArchitectureDoc() {
    const archDoc = path.join(GEMMEM_DIR, 'ARCHITECTURE.md');

    if (!fs.existsSync(archDoc)) {
        return;
    }

    try {
        let content = fs.readFileSync(archDoc, 'utf8');
        const today = new Date().toISOString().split('T')[0];

        // Update the "Last updated" line
        content = content.replace(
            /^> Last updated: .+$/m,
            `> Last updated: ${today}`
        );

        fs.writeFileSync(archDoc, content, 'utf8');
    } catch (err) {
        console.error('[memory] Warning: could not update ARCHITECTURE.md timestamp');
    }
}

// 3. Check for new lessons to log (from agent output)
function checkForLessons() {
    // This could parse agent output for patterns like "LESSON:" or "TIL:"
    // For now, just ensure the file exists
    const lessonsDoc = path.join(GEMMEM_DIR, 'LESSONS.md');

    if (!fs.existsSync(lessonsDoc)) {
        try {
            fs.mkdirSync(GEMMEM_DIR, { recursive: true });
            fs.writeFileSync(lessonsDoc, `# Lessons Learned

> Auto-updated by agents after implementation cycles.
> Last updated: ${new Date().toISOString().split('T')[0]}

## Entries

`, 'utf8');
        } catch {}
    }
}

// Main execution
async function main() {
    const startTime = Date.now();

    // Run all memory updates
    updateArchitectureMap();
    touchArchitectureDoc();
    checkForLessons();

    const elapsed = Date.now() - startTime;
    output('allow', `Memory updated (${elapsed}ms)`);
}

main();
