const fs = require('fs/promises');
const { createReadStream } = require('fs');
const path = require('path');
const readline = require('readline');

// --- Configuration (using smart path resolver and memory manager) ---
const paths = require('../../lib/paths');
const gemmem = require('../../lib/gemmem');
const ROOT_DIR = paths.workspace;

// Regex for files/dirs to completely ignore
const EXCLUDE_REGEX = /[\\/](bin|obj|node_modules|dist|build|coverage|\.git|\.vs|\.vscode|test-results|assets|public|wwwroot|mocks|__tests__|\.gemmem|\.gemini)[\\/]/;

// --- Parsers (Parallel Ready) ---

async function parseCsFile(filePath) {
    const stream = createReadStream(filePath, { encoding: 'utf8', highWaterMark: 2048 });
    const rl = readline.createInterface({ input: stream, crlfDelay: Infinity });

    try {
        let lines = 0;
        let namespace = null;
        let className = null;

        for await (const line of rl) {
            const nsMatch = line.match(/namespace\s+([\w\.]+)/);
            if (nsMatch) namespace = nsMatch[1];

            const classMatch = line.match(/(?:public|internal|private)?\s*(?:static|abstract|sealed)?\s*class\s+(\w+)/);
            if (classMatch && !className) className = classMatch[1];

            if (namespace && className) break;
            if (++lines > 100) break;
        }
        rl.close();
        stream.destroy();

        return {
            name: path.basename(filePath),
            namespace,
            className,
            type: 'cs'
        };
    } catch {
        return { name: path.basename(filePath), type: 'cs' };
    }
}

async function parseTsFile(filePath) {
    try {
        const content = await fs.readFile(filePath, 'utf8');
        const exports = [];
        const imports = [];

        // Find exports
        const exportRegex = /export\s+(?:const|function|class|type|interface|enum)\s+(\w+)/g;
        let match;
        while ((match = exportRegex.exec(content)) !== null) {
            if (!exports.includes(match[1])) exports.push(match[1]);
        }

        // Find imports (for dependency tracking)
        const importRegex = /import\s+.*?from\s+['"]([^'"]+)['"]/g;
        while ((match = importRegex.exec(content)) !== null) {
            const imp = match[1];
            // Only track local imports, not node_modules
            if (imp.startsWith('.') || imp.startsWith('@/')) {
                imports.push(imp);
            }
        }

        return {
            name: path.basename(filePath),
            exports,
            imports,
            type: 'ts'
        };
    } catch {
        return { name: path.basename(filePath), type: 'ts' };
    }
}

// --- Parallel Walker ---

async function scanFileSystem(dir) {
    const results = {
        csProjects: [],
        nodeProjects: [],
        csFiles: [],
        tsFiles: []
    };

    async function walk(currentDir) {
        let entries;
        try {
            entries = await fs.readdir(currentDir, { withFileTypes: true });
        } catch { return; }

        const pendingPromises = [];

        for (const entry of entries) {
            const fullPath = path.join(currentDir, entry.name);

            if (EXCLUDE_REGEX.test(fullPath)) continue;

            if (entry.isDirectory()) {
                pendingPromises.push(walk(fullPath));
            } else {
                const ext = path.extname(entry.name);
                if (ext === '.csproj') {
                    results.csProjects.push({ path: fullPath, dir: currentDir });
                } else if (entry.name === 'package.json') {
                    results.nodeProjects.push({ path: fullPath, dir: currentDir });
                } else if (ext === '.cs') {
                    results.csFiles.push({ path: fullPath, dir: currentDir });
                } else if (ext === '.ts' || ext === '.tsx') {
                    results.tsFiles.push({ path: fullPath, dir: currentDir });
                }
            }
        }

        await Promise.all(pendingPromises);
    }

    await walk(dir);
    return results;
}

// --- Classify Layer ---

function classifyLayer(filePath, namespace) {
    // Normalize to lowercase for matching
    const lower = filePath.toLowerCase().replace(/\\/g, '/');
    const ns = (namespace || '').toLowerCase();

    // Presentation layer
    if (lower.includes('/api/') || lower.includes('/controllers/') ||
        lower.includes('/routes/') || lower.includes('/pages/') ||
        lower.includes('/endpoints/') || lower.includes('/web/') ||
        ns.includes('.api') || ns.includes('.controllers') || ns.includes('.web')) {
        return 'presentation';
    }

    // Application layer
    if (lower.includes('/services/') || lower.includes('/application/') ||
        lower.includes('/usecases/') || lower.includes('/handlers/') ||
        lower.includes('/commands/') || lower.includes('/queries/') ||
        ns.includes('.services') || ns.includes('.application') || ns.includes('.handlers')) {
        return 'application';
    }

    // Domain layer
    if (lower.includes('/domain/') || lower.includes('/entities/') ||
        lower.includes('/models/') || lower.includes('/core/') ||
        lower.includes('/aggregates/') || lower.includes('/valueobjects/') ||
        ns.includes('.domain') || ns.includes('.entities') || ns.includes('.core')) {
        return 'domain';
    }

    // Infrastructure layer
    if (lower.includes('/infrastructure/') || lower.includes('/data/') ||
        lower.includes('/repositories/') || lower.includes('/external/') ||
        lower.includes('/persistence/') || lower.includes('/messaging/') ||
        lower.includes('/eventbus/') || lower.includes('/integrations/') ||
        ns.includes('.infrastructure') || ns.includes('.data') || ns.includes('.persistence')) {
        return 'infrastructure';
    }

    return 'unknown';
}

// --- Main ---

async function main() {
    const startTime = Date.now();

    // 1. Scan everything in one pass
    const scan = await scanFileSystem(ROOT_DIR);

    // 2. Process files in parallel
    const csTasks = scan.csFiles.map(async file => {
        file.parsed = await parseCsFile(file.path);
    });

    const tsTasks = scan.tsFiles.map(async file => {
        file.parsed = await parseTsFile(file.path);
    });

    await Promise.all([...csTasks, ...tsTasks]);

    // 3. Build snapshot structure
    const modules = {};
    const layers = {
        presentation: [],
        application: [],
        domain: [],
        infrastructure: [],
        unknown: []
    };
    const dependencies = [];

    // Sort projects by depth
    scan.csProjects.sort((a, b) => b.dir.length - a.dir.length);
    scan.nodeProjects.sort((a, b) => b.dir.length - a.dir.length);

    // Process C# projects
    for (const proj of scan.csProjects) {
        const projName = path.basename(proj.path, '.csproj');
        const relativePath = path.relative(ROOT_DIR, proj.dir).replace(/\\/g, '/');

        const projFiles = scan.csFiles.filter(f => f.path.startsWith(proj.dir));

        // Simplified file format: "FileName.cs (Namespace) -> ClassName/InterfaceName"
        const fileInfos = projFiles.map(f => {
            const exports = f.parsed.className || f.parsed.name.replace('.cs', '');
            return `${f.parsed.name} (${f.parsed.namespace || 'no-ns'}) -> ${exports}`;
        });

        modules[relativePath || projName] = {
            type: 'dotnet',
            namespace: projFiles[0]?.parsed?.namespace || projName,
            files: fileInfos
        };

        // Classify layer
        const layer = classifyLayer(proj.dir, projFiles[0]?.parsed?.namespace);
        if (layers[layer]) {
            layers[layer].push(relativePath || projName);
        }
    }

    // Process Node projects
    for (const proj of scan.nodeProjects) {
        let projName = path.basename(path.dirname(proj.path));
        try {
            const pkg = JSON.parse(await fs.readFile(proj.path, 'utf8'));
            if (pkg.name) projName = pkg.name;
        } catch {}

        const relativePath = path.relative(ROOT_DIR, proj.dir).replace(/\\/g, '/');

        const projFiles = scan.tsFiles.filter(f => f.path.startsWith(proj.dir));
        // Simplified file format: "FileName.ts -> export1, export2, ..."
        const fileInfos = projFiles.map(f => {
            const exports = (f.parsed.exports || []).join(', ') || 'default';
            return `${f.parsed.name} -> ${exports}`;
        });

        modules[relativePath || projName] = {
            type: 'typescript',
            name: projName,
            files: fileInfos
        };

        // Classify layer
        const layer = classifyLayer(proj.dir, null);
        if (layers[layer]) {
            layers[layer].push(relativePath || projName);
        }

        // Track dependencies from imports
        for (const file of projFiles) {
            if (file.parsed.imports) {
                for (const imp of file.parsed.imports) {
                    dependencies.push({
                        from: `${relativePath}/${file.parsed.name}`,
                        to: imp,
                        type: 'import'
                    });
                }
            }
        }
    }

    // Handle orphan files
    const assignedCsFiles = new Set(scan.csProjects.flatMap(p =>
        scan.csFiles.filter(f => f.path.startsWith(p.dir)).map(f => f.path)
    ));
    const orphanCs = scan.csFiles.filter(f => !assignedCsFiles.has(f.path));

    if (orphanCs.length > 0) {
        const byDir = {};
        for (const f of orphanCs) {
            const dir = path.relative(ROOT_DIR, f.dir).replace(/\\/g, '/') || 'root';
            if (!byDir[dir]) byDir[dir] = [];
            // Simplified format: "FileName.cs (Namespace) -> ClassName"
            const exports = f.parsed.className || f.parsed.name.replace('.cs', '');
            byDir[dir].push(`${f.parsed.name} (${f.parsed.namespace || 'no-ns'}) -> ${exports}`);
        }
        for (const [dir, files] of Object.entries(byDir)) {
            const moduleKey = `standalone-cs/${dir}`;
            modules[moduleKey] = {
                type: 'dotnet-standalone',
                files
            };

            // Classify layer for standalone modules too
            const layer = classifyLayer(dir, null);
            if (layers[layer]) {
                layers[layer].push(moduleKey);
            }
        }
    }

    const assignedTsFiles = new Set(scan.nodeProjects.flatMap(p =>
        scan.tsFiles.filter(f => f.path.startsWith(p.dir)).map(f => f.path)
    ));
    const orphanTs = scan.tsFiles.filter(f => !assignedTsFiles.has(f.path));

    if (orphanTs.length > 0) {
        const byDir = {};
        for (const f of orphanTs) {
            const dir = path.relative(ROOT_DIR, f.dir).replace(/\\/g, '/') || 'root';
            if (!byDir[dir]) byDir[dir] = [];
            // Simplified format: "FileName.ts -> export1, export2, ..."
            const exports = (f.parsed.exports || []).join(', ') || 'default';
            byDir[dir].push(`${f.parsed.name} -> ${exports}`);
        }
        for (const [dir, files] of Object.entries(byDir)) {
            modules[`standalone-ts/${dir}`] = {
                type: 'typescript-standalone',
                files
            };
        }
    }

    // 4. Update snapshot via gemmem
    const result = gemmem.updateSnapshot({
        modules,
        layers,
        dependencies
    });

    const elapsed = Date.now() - startTime;
    console.log(`Snapshot updated (${elapsed}ms) - ${result.modulesCount} modules`);
}

main().catch(err => console.error(err));
