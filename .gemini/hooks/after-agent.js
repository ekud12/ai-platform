#!/usr/bin/env node
/**
 * Unified AfterAgent hook - handles all post-agent tasks.
 *
 * Runs after every agent completes (wiggum or standalone).
 * Updates project memory: snapshot (architecture), history (lessons).
 *
 * Performance: ~100-200ms
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration (using smart path resolver and memory manager)
const paths = require('../lib/paths');
const gemmem = require('../lib/gemmem');
const WORKSPACE = paths.workspace;
const GEMINI_DIR = paths.gemini;

// Result helper
function output(decision, reason) {
    console.log(JSON.stringify({ decision, reason }));
}

// 0. Initialize .gemmem folder and files if they don't exist
function initializeGemmem() {
    const results = gemmem.initialize();

    if (results.folder === 'created') {
        console.error('[memory] Created .gemmem folder');
    }
    if (results.snapshot.action !== 'none') {
        console.error(`[memory] snapshot.json: ${results.snapshot.action}`);
    }
    if (results.history.action !== 'none') {
        console.error(`[memory] history.json: ${results.history.action}`);
    }
}

// 1. Update Architecture Snapshot
function updateSnapshot() {
    const mapScript = paths.resolveGemini('tools/docs/generate-map.js');

    if (!fs.existsSync(mapScript)) {
        console.error('[memory] generate-map.js not found, skipping snapshot');
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
        console.error('[memory] Warning: snapshot update failed');
    }
}

// 2. Parse agent output for lessons (LESSON: or TIL: patterns)
function extractLessonsFromOutput(output) {
    if (!output) return [];

    const lessons = [];
    const patterns = [
        /LESSON:\s*(.+?)(?:\n|$)/gi,
        /TIL:\s*(.+?)(?:\n|$)/gi,
        /LEARNED:\s*(.+?)(?:\n|$)/gi,
        /DECISION:\s*(.+?)(?:\n|$)/gi
    ];

    for (const pattern of patterns) {
        let match;
        while ((match = pattern.exec(output)) !== null) {
            const content = match[1].trim();
            if (content.length > 10) { // Skip very short entries
                lessons.push({
                    category: pattern.source.includes('DECISION') ? 'decision' : 'lesson',
                    title: content.slice(0, 100),
                    content: content,
                    source: 'agent-output'
                });
            }
        }
    }

    return lessons;
}

// 3. Check for and log new lessons
function processLessons() {
    // Check if agent passed output via env variable
    const agentOutput = process.env.AGENT_OUTPUT || '';
    const lessons = extractLessonsFromOutput(agentOutput);

    for (const lesson of lessons) {
        const result = gemmem.addHistoryEntry(lesson);
        if (result.success && !result.duplicate) {
            console.error(`[memory] Added lesson: ${lesson.title.slice(0, 50)}...`);
        }
    }
}

// Main execution
async function main() {
    const startTime = Date.now();

    // Initialize .gemmem folder if it doesn't exist (for new projects)
    initializeGemmem();

    // Run all memory updates
    updateSnapshot();
    processLessons();

    const elapsed = Date.now() - startTime;
    const stats = gemmem.getStats();
    output('allow', `Memory updated (${elapsed}ms) - ${stats.snapshot.modulesCount} modules, ${stats.history.entriesCount} entries`);
}

main();
