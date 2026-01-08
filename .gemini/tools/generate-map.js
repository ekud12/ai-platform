const fs = require('fs/promises');
const { createReadStream } = require('fs');
const path = require('path');
const readline = require('readline');

// --- Configuration ---
const ROOT_DIR = path.resolve(__dirname, '../../');
const MAP_FILE = path.join(ROOT_DIR, 'docs', 'ARCHITECTURE.md');
// Regex for files/dirs to completely ignore
const EXCLUDE_REGEX = /[\\/](bin|obj|node_modules|dist|build|coverage|\.git|\.vs|\.vscode|test-results|assets|public|wwwroot|mocks|__tests__)[\\/]/;

const HEADER = `# Architecture Map (Structural Memory)
*Auto-Generated: ${new Date().toISOString()}*

## Purpose
High-level dependency graph of the user code.

## Modules
`;

// --- Parsers (Parallel Ready) ---

async function parseCsFile(filePath) {
    // Read only the beginning of the file to find the namespace
    const stream = createReadStream(filePath, { encoding: 'utf8', highWaterMark: 2048 });
    const rl = readline.createInterface({ input: stream, crlfDelay: Infinity });

    try {
        let lines = 0;
        for await (const line of rl) {
            const match = line.match(/namespace\s+([\w\.]+)/);
            if (match) {
                rl.close();
                stream.destroy();
                return { name: path.basename(filePath), meta: `(${match[1]})` };
            }
            if (++lines > 50) break;
        }
        rl.close();
        stream.destroy();
    } catch {} // Ignore errors
    
    return { name: path.basename(filePath), meta: null };
}

async function parseTsFile(filePath) {
    try {
        // Read full file is usually faster than streaming for "search all" regex in Node
        const content = await fs.readFile(filePath, 'utf8');
        const exports = [];
        const regex = /export\s+(?:const|function|class|type|interface|enum)\s+(\w+)/g;
        let match;
        
        while ((match = regex.exec(content)) !== null) {
            // Simple dedup
            if (!exports.includes(match[1])) exports.push(match[1]);
        }
        
        const meta = exports.length > 0 ? `(Exports: ${exports.join(', ')})` : null;
        return { name: path.basename(filePath), meta };
    } catch {
        return { name: path.basename(filePath), meta: null };
    }
}

// --- Parallel Walker ---

async function scanFileSystem(dir) {
    // Flattened results
    const results = {
        csProjects: [],
        nodeProjects: [],
        csFiles: [],
        tsFiles: []
    };

    // Recursive Walker that runs in parallel
    async function walk(currentDir) {
        let entries;
        try {
            entries = await fs.readdir(currentDir, { withFileTypes: true });
        } catch { return; } // Ignore errors

        const pendingPromises = [];

        for (const entry of entries) {
            const fullPath = path.join(currentDir, entry.name);

            // 1. Check Exclusion (Fast Regex)
            if (EXCLUDE_REGEX.test(fullPath)) continue;

            if (entry.isDirectory()) {
                // Parallel recurse
                pendingPromises.push(walk(fullPath));
            } else {
                // File Classification
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

// --- Main ---

async function main() {
    console.time('Total Time');

    // 1. Scan EVERYTHING in one pass
    const scan = await scanFileSystem(ROOT_DIR);

    // 2. Process Files in Parallel (Blast IO)
    // We fire off parsing for all files immediately.
    const csTasks = scan.csFiles.map(async file => {
        const result = await parseCsFile(file.path);
        file.parsed = result;
    });
    
    const tsTasks = scan.tsFiles.map(async file => {
        const result = await parseTsFile(file.path);
        file.parsed = result;
    });

    // Wait for all IO to finish
    await Promise.all([...csTasks, ...tsTasks]);

    // 3. Organization (Memory)
    // Map files to their nearest project.
    // Logic: Find the project dir that is a prefix of the file dir, with the longest length (deepest).
    
    // Sort projects by directory length desc (deepest first) to ensure correct assignment
    scan.csProjects.sort((a, b) => b.dir.length - a.dir.length);
    scan.nodeProjects.sort((a, b) => b.dir.length - a.dir.length);

    const projectMap = new Map(); // ProjectPath -> [Files]

    // Initialize map
    for (const p of scan.csProjects) projectMap.set(p.path, []);
    for (const p of scan.nodeProjects) projectMap.set(p.path, []);

    // Track orphan files (no parent project)
    const orphanCs = [];
    const orphanTs = [];

    // Assign CS Files
    for (const file of scan.csFiles) {
        const parent = scan.csProjects.find(p => file.path.startsWith(p.dir));
        if (parent) {
            projectMap.get(parent.path).push(file);
        } else {
            orphanCs.push(file);
        }
    }

    // Assign TS Files
    for (const file of scan.tsFiles) {
        const parent = scan.nodeProjects.find(p => file.path.startsWith(p.dir));
        if (parent) {
            projectMap.get(parent.path).push(file);
        } else {
            orphanTs.push(file);
        }
    }

    // 4. Output Generation
    let output = HEADER;

    // Output C#
    for (const proj of scan.csProjects) {
        output += `\n### Project (C#): ${path.basename(proj.path)}\n`;
        const files = projectMap.get(proj.path);
        if (files) {
            for (const f of files) {
                output += `*   **${f.parsed.name}** ${f.parsed.meta || ''}\n`;
            }
        }
    }

    // Output Node
    for (const proj of scan.nodeProjects) {
        let name = path.basename(path.dirname(proj.path));
        // Try to read package.json name (fast read)
        try {
            const pkg = JSON.parse(await fs.readFile(proj.path, 'utf8'));
            if (pkg.name) name = pkg.name;
        } catch {} // Ignore errors

        output += `\n### Project (TS/JS): ${name}\n`;
        const files = projectMap.get(proj.path);
        if (files) {
            for (const f of files) {
                output += `*   **${f.parsed.name}** ${f.parsed.meta || ''}\n`;
            }
        }
    }

    // Output orphan C# files (no .csproj)
    if (orphanCs.length > 0) {
        output += `\n### Standalone C# Files (no .csproj)\n`;
        // Group by directory
        const byDir = {};
        for (const f of orphanCs) {
            const dir = path.relative(ROOT_DIR, f.dir) || '.';
            if (!byDir[dir]) byDir[dir] = [];
            byDir[dir].push(f);
        }
        for (const [dir, files] of Object.entries(byDir)) {
            output += `\n**${dir}/**\n`;
            for (const f of files) {
                output += `*   ${f.parsed.name} ${f.parsed.meta || ''}\n`;
            }
        }
    }

    // Output orphan TS files (no package.json)
    if (orphanTs.length > 0) {
        output += `\n### Standalone TS/JS Files (no package.json)\n`;
        const byDir = {};
        for (const f of orphanTs) {
            const dir = path.relative(ROOT_DIR, f.dir) || '.';
            if (!byDir[dir]) byDir[dir] = [];
            byDir[dir].push(f);
        }
        for (const [dir, files] of Object.entries(byDir)) {
            output += `\n**${dir}/**\n`;
            for (const f of files) {
                output += `*   ${f.parsed.name} ${f.parsed.meta || ''}\n`;
            }
        }
    }

    await fs.writeFile(MAP_FILE, output);
    console.log(`Map updated at ${MAP_FILE}`);
    console.timeEnd('Total Time');
}

main().catch(err => console.error(err));