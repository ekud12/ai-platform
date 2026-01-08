#!/usr/bin/env node
/**
 * AfterAgent hook - runs after agent completes.
 *
 * Currently minimal - can be extended for post-processing.
 */

function output(decision, reason) {
    console.log(JSON.stringify({ decision, reason }));
}

async function main() {
    output('allow', 'Agent completed');
}

main();
