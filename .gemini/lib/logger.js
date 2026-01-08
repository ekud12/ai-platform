#!/usr/bin/env node
/**
 * Simple file logger for milestone operations.
 *
 * Logs to .gemini/logs/ directory.
 * Creates daily log files: gemmem-YYYY-MM-DD.log
 */

const fs = require('fs');
const path = require('path');

// Get paths (lazy load)
let _paths = null;
function getPaths() {
    if (!_paths) {
        _paths = require('./paths');
    }
    return _paths;
}

// Get current timestamp
function getTimestamp() {
    return new Date().toISOString();
}

// Get today's date for file naming
function getToday() {
    return new Date().toISOString().split('T')[0];
}

/**
 * Ensure logs directory exists.
 */
function ensureLogsDir() {
    const paths = getPaths();
    const logsDir = paths.files.logs;

    if (!fs.existsSync(logsDir)) {
        fs.mkdirSync(logsDir, { recursive: true });
    }

    return logsDir;
}

/**
 * Get log file path for today.
 * @param {string} prefix - Log file prefix (e.g., 'gemmem', 'hook')
 */
function getLogFile(prefix = 'gemmem') {
    const logsDir = ensureLogsDir();
    return path.join(logsDir, `${prefix}-${getToday()}.log`);
}

/**
 * Append a log entry.
 * @param {string} level - Log level (INFO, WARN, ERROR)
 * @param {string} operation - Operation name
 * @param {string} message - Log message
 * @param {object} data - Optional additional data
 */
function log(level, operation, message, data = null) {
    const logFile = getLogFile();

    const entry = {
        timestamp: getTimestamp(),
        level,
        operation,
        message,
        ...(data && { data })
    };

    const line = JSON.stringify(entry) + '\n';

    try {
        fs.appendFileSync(logFile, line, 'utf8');
    } catch (err) {
        // Silent fail - logging shouldn't break operations
        console.error(`[logger] Failed to write log: ${err.message}`);
    }
}

/**
 * Log an info message.
 */
function info(operation, message, data = null) {
    log('INFO', operation, message, data);
}

/**
 * Log a warning message.
 */
function warn(operation, message, data = null) {
    log('WARN', operation, message, data);
}

/**
 * Log an error message.
 */
function error(operation, message, data = null) {
    log('ERROR', operation, message, data);
}

/**
 * Log a milestone event (always logged).
 * Milestones are significant events like initialization, updates, etc.
 */
function milestone(operation, message, data = null) {
    log('MILESTONE', operation, message, data);
}

/**
 * Clean up old log files (keep last N days).
 * @param {number} keepDays - Number of days to keep (default: 7)
 */
function cleanup(keepDays = 7) {
    const logsDir = ensureLogsDir();
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - keepDays);

    try {
        const files = fs.readdirSync(logsDir);

        for (const file of files) {
            if (!file.endsWith('.log')) continue;

            // Extract date from filename (prefix-YYYY-MM-DD.log)
            const match = file.match(/(\d{4}-\d{2}-\d{2})\.log$/);
            if (!match) continue;

            const fileDate = new Date(match[1]);
            if (fileDate < cutoffDate) {
                fs.unlinkSync(path.join(logsDir, file));
                console.error(`[logger] Cleaned up old log: ${file}`);
            }
        }
    } catch (err) {
        // Silent fail
    }
}

/**
 * Read recent log entries.
 * @param {number} count - Number of entries to return (default: 50)
 * @param {string} prefix - Log file prefix (default: 'gemmem')
 * @returns {Array} Recent log entries
 */
function readRecent(count = 50, prefix = 'gemmem') {
    const logFile = getLogFile(prefix);

    if (!fs.existsSync(logFile)) {
        return [];
    }

    try {
        const content = fs.readFileSync(logFile, 'utf8');
        const lines = content.trim().split('\n').filter(Boolean);

        return lines.slice(-count).map(line => {
            try {
                return JSON.parse(line);
            } catch {
                return { raw: line };
            }
        });
    } catch {
        return [];
    }
}

module.exports = {
    info,
    warn,
    error,
    milestone,
    cleanup,
    readRecent,
    getLogFile,
    ensureLogsDir
};
