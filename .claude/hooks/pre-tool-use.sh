#!/bin/bash
# Pre-tool-use hook: Enforce agent delegation for code files
# Blocks orchestrator from writing code directly - must delegate to specialized agents
#
# Delegation Rules:
#   .cs, .csproj, .sln         → dotnet-agent
#   .ts, .tsx, .js, .jsx       → typescript-agent
#   package.json, tsconfig.*   → typescript-agent
#
# This hook runs BEFORE tool execution. Exit 1 to block, exit 0 to allow.

set -euo pipefail

TOOL_NAME="${TOOL_NAME:-}"
FILE_PATH="${TOOL_FILE_PATH:-}"
AGENT_NAME="${CLAUDE_AGENT_NAME:-orchestrator}"

# Only intercept Write and Edit operations
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
    exit 0
fi

# Skip if no file path provided
if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

# Allow specialized agents to write their designated files
# Agents are identified by CLAUDE_AGENT_NAME environment variable
# Orchestrator is BLOCKED from writing code - must delegate
case "$AGENT_NAME" in
    dotnet-agent)
        # Allowed: .cs, .csproj, .sln, .fs, .fsproj, .vb, Directory.Build.props, global.json, nuget.config
        exit 0
        ;;
    typescript-agent)
        # Allowed: .ts, .tsx, .js, .jsx, .mjs, .cjs, package.json, tsconfig.*
        exit 0
        ;;
    observability-engineer)
        # Allowed: All code files (sets up instrumentation)
        exit 0
        ;;
    compliance-reviewer)
        # Allowed: All code files (fixes violations)
        exit 0
        ;;
    orchestrator)
        # BLOCKED: Orchestrator must delegate code work
        # Falls through to routing check below
        ;;
esac

# Extract filename and extension
FILENAME=$(basename "$FILE_PATH")
EXTENSION="${FILENAME##*.}"

# Define blocked extensions and their required agents
declare -A AGENT_ROUTING=(
    ["cs"]="dotnet-agent"
    ["csproj"]="dotnet-agent"
    ["sln"]="dotnet-agent"
    ["fs"]="dotnet-agent"
    ["fsproj"]="dotnet-agent"
    ["vb"]="dotnet-agent"
    ["ts"]="typescript-agent"
    ["tsx"]="typescript-agent"
    ["js"]="typescript-agent"
    ["jsx"]="typescript-agent"
    ["mjs"]="typescript-agent"
    ["cjs"]="typescript-agent"
)

# Check for specific filenames that require delegation
declare -A FILENAME_ROUTING=(
    ["package.json"]="typescript-agent"
    ["tsconfig.json"]="typescript-agent"
    ["tsconfig.build.json"]="typescript-agent"
    ["tsconfig.test.json"]="typescript-agent"
    [".eslintrc.json"]="typescript-agent"
    ["Directory.Build.props"]="dotnet-agent"
    ["Directory.Packages.props"]="dotnet-agent"
    ["global.json"]="dotnet-agent"
    ["nuget.config"]="dotnet-agent"
)

# Check filename-specific routing first
if [[ -v "FILENAME_ROUTING[$FILENAME]" ]]; then
    REQUIRED_AGENT="${FILENAME_ROUTING[$FILENAME]}"
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  DELEGATION REQUIRED                                             ║"
    echo "╠══════════════════════════════════════════════════════════════════╣"
    echo "║  File: $FILENAME"
    echo "║  Required Agent: $REQUIRED_AGENT"
    echo "║                                                                  ║"
    echo "║  Orchestrator cannot write this file directly.                   ║"
    echo "║  Delegate this task to the specialized agent.                    ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    exit 1
fi

# Check extension-based routing
if [[ -v "AGENT_ROUTING[$EXTENSION]" ]]; then
    REQUIRED_AGENT="${AGENT_ROUTING[$EXTENSION]}"
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  DELEGATION REQUIRED                                             ║"
    echo "╠══════════════════════════════════════════════════════════════════╣"
    echo "║  File: $FILENAME"
    echo "║  Extension: .$EXTENSION"
    echo "║  Required Agent: $REQUIRED_AGENT"
    echo "║                                                                  ║"
    echo "║  Orchestrator cannot write code files directly.                  ║"
    echo "║  Delegate this task to the specialized agent.                    ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    exit 1
fi

# Allow all other files (markdown, yaml, config, etc.)
exit 0
