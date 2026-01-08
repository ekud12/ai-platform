#!/usr/bin/env node
/**
 * Gemmem (Gemini Memory) Manager
 *
 * Handles initialization, reading, and updating of project memory files.
 * Uses JSON for fast parsing and structured updates.
 *
 * Files:
 * - snapshot.json: Point-in-time architecture snapshot (modules, layers, dependencies)
 * - history.json: Append-only log of lessons learned and decisions
 *
 * States handled:
 * - No folder exists
 * - Folder exists but no files
 * - Files exist but are empty
 * - Files exist but are corrupted/invalid JSON
 * - Files exist with content (merge/update)
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// File names
const SNAPSHOT_FILE = 'snapshot.json';
const HISTORY_FILE = 'history.json';

// Get paths (lazy load to avoid circular deps)
let _paths = null;
function getPaths() {
    if (!_paths) {
        _paths = require('./paths');
    }
    return _paths;
}

// Get logger (lazy load)
let _logger = null;
function getLogger() {
    if (!_logger) {
        try {
            _logger = require('./logger');
        } catch {
            // Fallback if logger not available
            _logger = {
                milestone: () => {},
                info: () => {},
                warn: () => {},
                error: () => {}
            };
        }
    }
    return _logger;
}

// Get today's date in ISO format
function getToday() {
    return new Date().toISOString().split('T')[0];
}

// Generate a short hash for deduplication
function hashContent(content) {
    return crypto.createHash('md5').update(content).digest('hex').slice(0, 8);
}

// Default schema for snapshot.json (architecture snapshot)
function getSnapshotDefaults() {
    return {
        version: '1.0',
        lastUpdated: getToday(),
        generatedBy: 'gemmem',
        modules: {},
        layers: {
            presentation: [],
            application: [],
            domain: [],
            infrastructure: []
        },
        dependencies: []
    };
}

// Default schema for history.json (lessons/decisions log)
function getHistoryDefaults() {
    return {
        version: '1.0',
        lastUpdated: getToday(),
        entries: []
    };
}

/**
 * Initialize or repair a JSON file with proper state handling.
 *
 * @param {string} filePath - Path to the JSON file
 * @param {object} defaults - Default content structure
 * @returns {{ status: string, action: string }} Result of initialization
 */
function initializeJsonFile(filePath, defaults) {
    const result = { status: 'ok', action: 'none' };

    // Case 1: File doesn't exist - create with defaults
    if (!fs.existsSync(filePath)) {
        fs.writeFileSync(filePath, JSON.stringify(defaults, null, 2), 'utf8');
        result.action = 'created';
        return result;
    }

    // Read existing content
    let content;
    try {
        content = fs.readFileSync(filePath, 'utf8');
    } catch (err) {
        // Can't read file - recreate
        fs.writeFileSync(filePath, JSON.stringify(defaults, null, 2), 'utf8');
        result.action = 'recreated';
        result.reason = 'unreadable';
        return result;
    }

    // Case 2: File exists but is empty
    const trimmed = content.trim();
    if (!trimmed) {
        fs.writeFileSync(filePath, JSON.stringify(defaults, null, 2), 'utf8');
        result.action = 'initialized';
        result.reason = 'empty';
        return result;
    }

    // Case 3: Try to parse JSON
    let parsed;
    try {
        parsed = JSON.parse(trimmed);
    } catch (err) {
        // Invalid JSON - backup and recreate
        const backupPath = filePath + '.bak.' + Date.now();
        fs.copyFileSync(filePath, backupPath);
        fs.writeFileSync(filePath, JSON.stringify(defaults, null, 2), 'utf8');
        result.action = 'repaired';
        result.reason = 'invalid_json';
        result.backup = backupPath;
        return result;
    }

    // Case 4: Valid JSON - check for missing required fields
    if (typeof parsed !== 'object' || parsed === null) {
        fs.writeFileSync(filePath, JSON.stringify(defaults, null, 2), 'utf8');
        result.action = 'repaired';
        result.reason = 'not_object';
        return result;
    }

    // Merge missing top-level fields from defaults
    let needsUpdate = false;
    for (const key of Object.keys(defaults)) {
        if (!(key in parsed)) {
            parsed[key] = defaults[key];
            needsUpdate = true;
        }
    }

    if (needsUpdate) {
        fs.writeFileSync(filePath, JSON.stringify(parsed, null, 2), 'utf8');
        result.action = 'merged';
        result.reason = 'missing_fields';
    }

    return result;
}

/**
 * Initialize the .gemmem folder and all memory files.
 *
 * @returns {{ folder: string, snapshot: object, history: object }}
 */
function initialize() {
    const paths = getPaths();
    const logger = getLogger();
    const gemmemDir = paths.gemmem;
    const results = { folder: 'exists' };

    // Ensure folder exists
    if (!fs.existsSync(gemmemDir)) {
        fs.mkdirSync(gemmemDir, { recursive: true });
        results.folder = 'created';
        logger.milestone('gemmem.initialize', 'Created .gemmem folder', { path: gemmemDir });
    }

    // Initialize snapshot.json (architecture)
    const snapshotFile = path.join(gemmemDir, SNAPSHOT_FILE);
    results.snapshot = initializeJsonFile(snapshotFile, getSnapshotDefaults());
    if (results.snapshot.action !== 'none') {
        logger.milestone('gemmem.initialize', `Snapshot file: ${results.snapshot.action}`, results.snapshot);
    }

    // Initialize history.json (lessons)
    const historyFile = path.join(gemmemDir, HISTORY_FILE);
    results.history = initializeJsonFile(historyFile, getHistoryDefaults());
    if (results.history.action !== 'none') {
        logger.milestone('gemmem.initialize', `History file: ${results.history.action}`, results.history);
    }

    return results;
}

/**
 * Read snapshot data (architecture).
 *
 * @returns {object|null} Snapshot data or null if unavailable
 */
function readSnapshot() {
    const paths = getPaths();
    const snapshotFile = path.join(paths.gemmem, SNAPSHOT_FILE);

    if (!fs.existsSync(snapshotFile)) {
        return null;
    }

    try {
        const content = fs.readFileSync(snapshotFile, 'utf8').trim();
        return content ? JSON.parse(content) : null;
    } catch {
        return null;
    }
}

/**
 * Update snapshot data (full replacement of modules/layers).
 *
 * @param {object} data - New snapshot data (modules, layers, dependencies)
 * @returns {{ success: boolean, modulesCount: number }}
 */
function updateSnapshot(data) {
    const paths = getPaths();
    const logger = getLogger();
    const snapshotFile = path.join(paths.gemmem, SNAPSHOT_FILE);

    // Ensure file exists
    initialize();

    try {
        const current = readSnapshot() || getSnapshotDefaults();

        // Update with new data
        current.lastUpdated = getToday();
        if (data.modules) current.modules = data.modules;
        if (data.layers) current.layers = data.layers;
        if (data.dependencies) current.dependencies = data.dependencies;

        fs.writeFileSync(snapshotFile, JSON.stringify(current, null, 2), 'utf8');

        const modulesCount = Object.keys(current.modules).length;
        const depsCount = (current.dependencies || []).length;

        logger.milestone('gemmem.updateSnapshot', 'Architecture snapshot updated', {
            modulesCount,
            dependenciesCount: depsCount,
            layers: Object.keys(current.layers).filter(k => current.layers[k].length > 0)
        });

        return {
            success: true,
            modulesCount
        };
    } catch (err) {
        logger.error('gemmem.updateSnapshot', 'Failed to update snapshot', { error: err.message });
        return { success: false, error: err.message };
    }
}

/**
 * Read history data (lessons/decisions).
 *
 * @returns {object|null} History data or null if unavailable
 */
function readHistory() {
    const paths = getPaths();
    const historyFile = path.join(paths.gemmem, HISTORY_FILE);

    if (!fs.existsSync(historyFile)) {
        return null;
    }

    try {
        const content = fs.readFileSync(historyFile, 'utf8').trim();
        return content ? JSON.parse(content) : null;
    } catch {
        return null;
    }
}

/**
 * Add a new history entry (with deduplication).
 *
 * @param {object} entry - History entry { category, title, content, source? }
 * @returns {{ success: boolean, id?: string, duplicate?: boolean }}
 */
function addHistoryEntry(entry) {
    const paths = getPaths();
    const logger = getLogger();
    const historyFile = path.join(paths.gemmem, HISTORY_FILE);

    // Ensure file exists
    initialize();

    try {
        const current = readHistory() || getHistoryDefaults();

        // Generate content hash for deduplication
        const contentHash = hashContent(entry.title + entry.content);

        // Check for duplicates
        const isDuplicate = current.entries.some(e => e.hash === contentHash);
        if (isDuplicate) {
            logger.info('gemmem.addHistoryEntry', 'Duplicate entry skipped', { hash: contentHash });
            return { success: true, duplicate: true };
        }

        // Create new entry
        const newEntry = {
            id: `entry-${Date.now()}`,
            hash: contentHash,
            date: getToday(),
            category: entry.category || 'general',
            title: entry.title,
            content: entry.content,
            source: entry.source || 'agent'
        };

        current.entries.push(newEntry);
        current.lastUpdated = getToday();

        fs.writeFileSync(historyFile, JSON.stringify(current, null, 2), 'utf8');

        logger.milestone('gemmem.addHistoryEntry', 'New history entry added', {
            id: newEntry.id,
            category: newEntry.category,
            title: newEntry.title.slice(0, 50)
        });

        return { success: true, id: newEntry.id };
    } catch (err) {
        logger.error('gemmem.addHistoryEntry', 'Failed to add entry', { error: err.message });
        return { success: false, error: err.message };
    }
}

/**
 * Get history entries by category.
 *
 * @param {string} category - Category to filter by
 * @returns {Array} Matching entries
 */
function getHistoryByCategory(category) {
    const data = readHistory();
    if (!data || !data.entries) return [];
    return data.entries.filter(e => e.category === category);
}

/**
 * Get recent history entries (last N).
 *
 * @param {number} count - Number of entries to return (default: 10)
 * @returns {Array} Recent entries
 */
function getRecentHistory(count = 10) {
    const data = readHistory();
    if (!data || !data.entries) return [];
    return data.entries.slice(-count);
}

/**
 * Get summary statistics.
 *
 * @returns {object} Summary stats
 */
function getStats() {
    const snapshot = readSnapshot();
    const history = readHistory();

    return {
        snapshot: {
            modulesCount: snapshot ? Object.keys(snapshot.modules).length : 0,
            lastUpdated: snapshot?.lastUpdated || null
        },
        history: {
            entriesCount: history?.entries?.length || 0,
            lastUpdated: history?.lastUpdated || null,
            categories: history?.entries
                ? [...new Set(history.entries.map(e => e.category))]
                : []
        }
    };
}

module.exports = {
    // Constants
    SNAPSHOT_FILE,
    HISTORY_FILE,
    // Core
    initialize,
    getStats,
    // Snapshot (architecture)
    readSnapshot,
    updateSnapshot,
    // History (lessons/decisions)
    readHistory,
    addHistoryEntry,
    getHistoryByCategory,
    getRecentHistory,
    // Expose for testing
    initializeJsonFile,
    getSnapshotDefaults,
    getHistoryDefaults
};
