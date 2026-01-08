/**
 * Smart Path Resolver for Node.js scripts.
 *
 * Supports multiple environments:
 * - Local development (relative paths)
 * - CI/CD pipelines (environment variables)
 * - Docker containers (mounted volumes)
 *
 * Environment Variables (all optional):
 * - WORKSPACE_ROOT: Override workspace root directory
 * - GEMINI_DIR: Override .gemini directory location
 * - GEMMEM_DIR: Override .gemmem directory location
 * - GEMINI_PROJECT_DIR: Legacy support (Gemini CLI)
 *
 * Usage:
 *   const paths = require('../lib/paths');
 *   console.log(paths.workspace);    // /app or C:\Projects\ai-platform
 *   console.log(paths.gemmem);       // /app/.gemmem
 *   console.log(paths.gemini);       // /app/.gemini
 *   console.log(paths.resolve('src/index.ts')); // Full path to file
 */

const path = require('path');
const fs = require('fs');

/**
 * Detect workspace root by searching for marker files/folders.
 * Walks up from startDir until it finds a workspace marker.
 */
function detectWorkspaceRoot(startDir) {
    const markers = ['.gemini', '.git', 'package.json', '*.sln'];
    let current = startDir;
    let previous = null;

    while (current !== previous) {
        // Check for .gemini folder (strongest indicator)
        if (fs.existsSync(path.join(current, '.gemini'))) {
            return current;
        }

        // Check for .git folder
        if (fs.existsSync(path.join(current, '.git'))) {
            return current;
        }

        // Check for solution file (Windows .NET projects)
        try {
            const files = fs.readdirSync(current);
            if (files.some(f => f.endsWith('.sln'))) {
                return current;
            }
        } catch {}

        previous = current;
        current = path.dirname(current);
    }

    // Fallback: assume we're somewhere in the workspace
    return startDir;
}

/**
 * Resolve the workspace root directory.
 * Priority: ENV > Detection > Fallback
 */
function resolveWorkspace() {
    // 1. Check explicit environment variable
    if (process.env.WORKSPACE_ROOT) {
        return path.resolve(process.env.WORKSPACE_ROOT);
    }

    // 2. Check Gemini CLI environment variable (legacy support)
    if (process.env.GEMINI_PROJECT_DIR) {
        return path.resolve(process.env.GEMINI_PROJECT_DIR);
    }

    // 3. Check GitHub Actions workspace
    if (process.env.GITHUB_WORKSPACE) {
        return path.resolve(process.env.GITHUB_WORKSPACE);
    }

    // 4. Check Azure DevOps workspace
    if (process.env.BUILD_SOURCESDIRECTORY) {
        return path.resolve(process.env.BUILD_SOURCESDIRECTORY);
    }

    // 5. Check GitLab CI workspace
    if (process.env.CI_PROJECT_DIR) {
        return path.resolve(process.env.CI_PROJECT_DIR);
    }

    // 6. Auto-detect from current file location
    // __dirname is .gemini/lib/, so workspace is ../../
    const scriptDir = __dirname;
    const detected = detectWorkspaceRoot(scriptDir);

    if (detected !== scriptDir) {
        return detected;
    }

    // 7. Fallback: two levels up from this script
    return path.resolve(__dirname, '../../');
}

/**
 * Resolve the .gemini directory.
 */
function resolveGeminiDir(workspace) {
    if (process.env.GEMINI_DIR) {
        return path.resolve(process.env.GEMINI_DIR);
    }
    return path.join(workspace, '.gemini');
}

/**
 * Resolve the .gemmem directory (architecture & lessons).
 */
function resolveGemmemDir(workspace) {
    if (process.env.GEMMEM_DIR) {
        return path.resolve(process.env.GEMMEM_DIR);
    }
    return path.join(workspace, '.gemmem');
}

// Compute paths once at module load
const workspace = resolveWorkspace();
const gemini = resolveGeminiDir(workspace);
const gemmem = resolveGemmemDir(workspace);

/**
 * Exported paths object.
 */
const paths = {
    /** Workspace root directory */
    workspace,

    /** .gemini directory (OS configuration) */
    gemini,

    /** .gemmem directory (architecture & lessons) */
    gemmem,

    /** Key files */
    files: {
        architecture: path.join(gemmem, 'ARCHITECTURE.md'),
        lessons: path.join(gemmem, 'LESSONS.md'),
        rules: path.join(gemini, 'rules'),
        compiledRules: path.join(gemini, 'rules', 'compiled'),
        hooks: path.join(gemini, 'hooks'),
        tools: path.join(gemini, 'tools'),
        logs: path.join(gemini, 'logs'),
    },

    /**
     * Resolve a path relative to workspace root.
     * @param {string} relativePath - Path relative to workspace
     * @returns {string} Absolute path
     */
    resolve(relativePath) {
        return path.join(workspace, relativePath);
    },

    /**
     * Resolve a path relative to .gemini directory.
     * @param {string} relativePath - Path relative to .gemini
     * @returns {string} Absolute path
     */
    resolveGemini(relativePath) {
        return path.join(gemini, relativePath);
    },

    /**
     * Resolve a path relative to .gemmem directory.
     * @param {string} relativePath - Path relative to .gemmem
     * @returns {string} Absolute path
     */
    resolveGemmem(relativePath) {
        return path.join(gemmem, relativePath);
    },

    /**
     * Check if running in CI environment.
     * @returns {boolean}
     */
    isCI() {
        return !!(
            process.env.CI ||
            process.env.GITHUB_ACTIONS ||
            process.env.TF_BUILD ||
            process.env.GITLAB_CI ||
            process.env.JENKINS_URL
        );
    },

    /**
     * Check if running in Docker container.
     * @returns {boolean}
     */
    isDocker() {
        try {
            // Check for .dockerenv file
            if (fs.existsSync('/.dockerenv')) return true;

            // Check cgroup for docker
            const cgroup = fs.readFileSync('/proc/1/cgroup', 'utf8');
            return cgroup.includes('docker');
        } catch {
            return false;
        }
    },

    /**
     * Get environment info for debugging.
     * @returns {object}
     */
    getEnvironmentInfo() {
        return {
            workspace,
            gemini,
            gemmem,
            isCI: this.isCI(),
            isDocker: this.isDocker(),
            platform: process.platform,
            env: {
                WORKSPACE_ROOT: process.env.WORKSPACE_ROOT || '(not set)',
                GEMINI_PROJECT_DIR: process.env.GEMINI_PROJECT_DIR || '(not set)',
                GEMINI_DIR: process.env.GEMINI_DIR || '(not set)',
                GEMMEM_DIR: process.env.GEMMEM_DIR || '(not set)',
            }
        };
    }
};

module.exports = paths;
