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
 * - GEMINI_PROJECT_DIR: Legacy support (Gemini CLI)
 */

const path = require('path');
const fs = require('fs');

/**
 * Detect workspace root by searching for marker files/folders.
 */
function detectWorkspaceRoot(startDir) {
    let current = startDir;
    let previous = null;

    while (current !== previous) {
        if (fs.existsSync(path.join(current, '.gemini'))) {
            return current;
        }
        if (fs.existsSync(path.join(current, '.git'))) {
            return current;
        }
        try {
            const files = fs.readdirSync(current);
            if (files.some(f => f.endsWith('.sln'))) {
                return current;
            }
        } catch {}

        previous = current;
        current = path.dirname(current);
    }

    return startDir;
}

/**
 * Resolve the workspace root directory.
 */
function resolveWorkspace() {
    if (process.env.WORKSPACE_ROOT) {
        return path.resolve(process.env.WORKSPACE_ROOT);
    }
    if (process.env.GEMINI_PROJECT_DIR) {
        return path.resolve(process.env.GEMINI_PROJECT_DIR);
    }
    if (process.env.GITHUB_WORKSPACE) {
        return path.resolve(process.env.GITHUB_WORKSPACE);
    }
    if (process.env.BUILD_SOURCESDIRECTORY) {
        return path.resolve(process.env.BUILD_SOURCESDIRECTORY);
    }
    if (process.env.CI_PROJECT_DIR) {
        return path.resolve(process.env.CI_PROJECT_DIR);
    }

    const scriptDir = __dirname;
    const detected = detectWorkspaceRoot(scriptDir);
    return detected !== scriptDir ? detected : path.resolve(__dirname, '../../');
}

function resolveGeminiDir(workspace) {
    if (process.env.GEMINI_DIR) {
        return path.resolve(process.env.GEMINI_DIR);
    }
    return path.join(workspace, '.gemini');
}

const workspace = resolveWorkspace();
const gemini = resolveGeminiDir(workspace);

const paths = {
    workspace,
    gemini,

    files: {
        rules: path.join(gemini, 'knowledge'),
        compiledRules: path.join(gemini, 'knowledge', 'compiled'),
        hooks: path.join(gemini, 'hooks'),
        skills: path.join(gemini, 'skills'),
    },

    resolve(relativePath) {
        return path.join(workspace, relativePath);
    },

    resolveGemini(relativePath) {
        return path.join(gemini, relativePath);
    },

    isCI() {
        return !!(
            process.env.CI ||
            process.env.GITHUB_ACTIONS ||
            process.env.TF_BUILD ||
            process.env.GITLAB_CI ||
            process.env.JENKINS_URL
        );
    },

    isDocker() {
        try {
            if (fs.existsSync('/.dockerenv')) return true;
            const cgroup = fs.readFileSync('/proc/1/cgroup', 'utf8');
            return cgroup.includes('docker');
        } catch {
            return false;
        }
    },

    getEnvironmentInfo() {
        return {
            workspace,
            gemini,
            isCI: this.isCI(),
            isDocker: this.isDocker(),
            platform: process.platform,
        };
    }
};

module.exports = paths;
