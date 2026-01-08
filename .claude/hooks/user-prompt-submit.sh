#!/bin/bash
# User-prompt-submit hook: Intelligent request routing and agent orchestration
# Analyzes user requests and provides routing guidance
#
# Agent Hierarchy:
#   orchestrator                 → Entry point, coordinates workflows, NEVER writes code
#
# Specialized Agents (invoked by orchestrator):
#   dotnet-agent                 → C#/.NET code generation
#   typescript-agent             → TypeScript/JS code generation
#   architect                    → Pre-implementation design validation
#   observability-engineer       → Logging, tracing, metrics infrastructure
#   compliance-reviewer          → Post-implementation validation

set -euo pipefail

PROMPT="${USER_PROMPT:-}"
PROMPT_LOWER=$(echo "$PROMPT" | tr '[:upper:]' '[:lower:]')

# Track which agents to suggest
declare -a SUGGESTED_AGENTS=()
declare -a ROUTING_REASONS=()

# ═══════════════════════════════════════════════════════════════════════════════
# DETECTION: .NET/C# Code Requests
# ═══════════════════════════════════════════════════════════════════════════════
if [[ "$PROMPT_LOWER" =~ (\.cs|csharp|c#|\.net|dotnet|aspnet|asp\.net|entity\ framework|efcore|nuget|csproj|blazor|maui|minimal\ api) ]]; then
    SUGGESTED_AGENTS+=("dotnet-agent")
    ROUTING_REASONS+=(".NET/C# code generation detected")
fi

# ═══════════════════════════════════════════════════════════════════════════════
# DETECTION: TypeScript/JavaScript Code Requests
# ═══════════════════════════════════════════════════════════════════════════════
if [[ "$PROMPT_LOWER" =~ (\.ts|\.tsx|\.js|\.jsx|typescript|javascript|node|npm|yarn|pnpm|react|vue|angular|next|express|package\.json|tsconfig) ]]; then
    SUGGESTED_AGENTS+=("typescript-agent")
    ROUTING_REASONS+=("TypeScript/JavaScript code generation detected")
fi

# ═══════════════════════════════════════════════════════════════════════════════
# DETECTION: Architecture/Design Requests (Pre-Implementation)
# ═══════════════════════════════════════════════════════════════════════════════
if [[ "$PROMPT_LOWER" =~ (architect|design|system|microservice|distributed|scale|boundary|domain|integration|api\ design|event\ driven|cqrs|event\ sourcing) ]]; then
    if [[ "$PROMPT_LOWER" =~ (implement|build|create|add|new|feature|service|component) ]]; then
        SUGGESTED_AGENTS+=("architect")
        ROUTING_REASONS+=("Significant feature - architecture review recommended before implementation")
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# DETECTION: Observability Infrastructure Requests
# ═══════════════════════════════════════════════════════════════════════════════
if [[ "$PROMPT_LOWER" =~ (logging|metrics|tracing|telemetry|observability|monitoring|opentelemetry|serilog|health\ check|diagnostics|instrumentation) ]]; then
    SUGGESTED_AGENTS+=("observability-engineer")
    ROUTING_REASONS+=("Observability infrastructure setup detected")
fi

# ═══════════════════════════════════════════════════════════════════════════════
# DETECTION: Completion/Review Signals (Post-Implementation)
# ═══════════════════════════════════════════════════════════════════════════════
if [[ "$PROMPT_LOWER" =~ (done|ready|finished|complete|merge|ship|deploy|review|validate|check\ compliance|pr\ ready) ]]; then
    SUGGESTED_AGENTS+=("compliance-reviewer")
    ROUTING_REASONS+=("Completion signal - compliance review recommended")
fi

# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT: Routing Guidance
# ═══════════════════════════════════════════════════════════════════════════════
if [[ ${#SUGGESTED_AGENTS[@]} -gt 0 ]]; then
    echo ""
    echo "┌─────────────────────────────────────────────────────────────────────┐"
    echo "│  AGENT ROUTING GUIDANCE                                             │"
    echo "├─────────────────────────────────────────────────────────────────────┤"

    for i in "${!SUGGESTED_AGENTS[@]}"; do
        AGENT="${SUGGESTED_AGENTS[$i]}"
        REASON="${ROUTING_REASONS[$i]}"

        case "$AGENT" in
            dotnet-agent)
                ICON="⚙️"
                ;;
            typescript-agent)
                ICON="📘"
                ;;
            architect)
                ICON="🏗️"
                ;;
            observability-engineer)
                ICON="📊"
                ;;
            compliance-reviewer)
                ICON="✅"
                ;;
            *)
                ICON="🔧"
                ;;
        esac

        printf "│  %s %-20s │ %s\n" "$ICON" "$AGENT" "$REASON"
    done

    echo "├─────────────────────────────────────────────────────────────────────┤"
    echo "│  🎯 For complex workflows: use orchestrator agent                   │"
    echo "│  📝 For single tasks: delegate directly to specialized agent        │"
    echo "│  ⛔ NEVER write code directly - always delegate to agents           │"
    echo "└─────────────────────────────────────────────────────────────────────┘"
    echo ""
fi

exit 0
