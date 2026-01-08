#!/bin/bash
# Post-tool-use hook: Code formatting and validation after Write/Edit operations
# Runs AFTER successful tool execution to ensure consistent formatting
#
# Formatting Rules:
#   .cs files        → dotnet format
#   .ts/.tsx/.js     → prettier
#   .json files      → prettier
#   .csproj/.xml     → (preserved as-is, manual formatting)

set -euo pipefail

TOOL_NAME="${TOOL_NAME:-}"
FILE_PATH="${TOOL_FILE_PATH:-}"

# Only run for Write and Edit operations
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
    exit 0
fi

# Skip if no file path
if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

# Skip if file doesn't exist (failed write)
if [[ ! -f "$FILE_PATH" ]]; then
    exit 0
fi

# Extract extension
FILENAME=$(basename "$FILE_PATH")
EXTENSION="${FILENAME##*.}"

# ═══════════════════════════════════════════════════════════════════════════════
# FORMAT: C# Files
# ═══════════════════════════════════════════════════════════════════════════════
if [[ "$EXTENSION" == "cs" ]]; then
    if command -v dotnet &> /dev/null; then
        # Try to find the nearest .csproj or .sln for context
        DIR=$(dirname "$FILE_PATH")
        while [[ "$DIR" != "/" && "$DIR" != "." ]]; do
            if ls "$DIR"/*.csproj 1> /dev/null 2>&1 || ls "$DIR"/*.sln 1> /dev/null 2>&1; then
                dotnet format "$DIR" --include "$FILE_PATH" 2>/dev/null || true
                break
            fi
            DIR=$(dirname "$DIR")
        done
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# FORMAT: TypeScript/JavaScript Files
# ═══════════════════════════════════════════════════════════════════════════════
if [[ "$EXTENSION" =~ ^(ts|tsx|js|jsx|mjs|cjs)$ ]]; then
    if command -v prettier &> /dev/null; then
        prettier --write "$FILE_PATH" 2>/dev/null || true
    elif command -v npx &> /dev/null; then
        npx prettier --write "$FILE_PATH" 2>/dev/null || true
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# FORMAT: JSON Files
# ═══════════════════════════════════════════════════════════════════════════════
if [[ "$EXTENSION" == "json" ]]; then
    if command -v prettier &> /dev/null; then
        prettier --write "$FILE_PATH" 2>/dev/null || true
    elif command -v npx &> /dev/null; then
        npx prettier --write "$FILE_PATH" 2>/dev/null || true
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATE: Check for forbidden patterns in generated code
# ═══════════════════════════════════════════════════════════════════════════════
if [[ "$EXTENSION" =~ ^(cs|ts|tsx|js|jsx)$ ]]; then
    # Check for TODO comments (forbidden in production code)
    if grep -q "TODO" "$FILE_PATH" 2>/dev/null; then
        echo ""
        echo "⚠️  WARNING: TODO comment detected in $FILENAME"
        echo "   Production code should not contain TODO placeholders."
        echo ""
    fi

    # Check for console.log in TypeScript/JavaScript (forbidden)
    if [[ "$EXTENSION" =~ ^(ts|tsx|js|jsx)$ ]]; then
        if grep -q "console\." "$FILE_PATH" 2>/dev/null; then
            echo ""
            echo "⚠️  WARNING: console.* detected in $FILENAME"
            echo "   Use structured logging instead of console statements."
            echo ""
        fi
    fi
fi

exit 0
