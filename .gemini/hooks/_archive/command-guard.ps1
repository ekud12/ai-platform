<#
.SYNOPSIS
    Command sandbox guard for Gemini CLI.
    Validates shell commands against allow/block lists before execution.

.DESCRIPTION
    This hook intercepts all shell/bash tool calls from Gemini CLI and validates
    them against configurable patterns in blocked-commands.json.

    Returns JSON with decision: "allow", "block", or "ask"

.NOTES
    Part of the AI-OS sandbox system.
    Version: 1.0
#>

param(
    [Parameter(ValueFromPipeline = $true)]
    [string]$InputJson
)

$ErrorActionPreference = "Stop"

# Get script directory and config path
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$configPath = Join-Path $scriptDir "blocked-commands.json"
$logDir = Join-Path (Split-Path -Parent $scriptDir) "logs"

# Helper function to write response
function Write-Decision {
    param(
        [string]$Decision,
        [string]$Reason,
        [string]$Command = ""
    )

    $result = @{
        decision = $Decision
        reason   = $Reason
    }

    # Log blocked commands if enabled
    if ($Decision -eq "block" -and $config.settings.log_blocked_commands) {
        try {
            if (-not (Test-Path $logDir)) {
                New-Item -ItemType Directory -Path $logDir -Force | Out-Null
            }
            $logFile = Join-Path $logDir "blocked-commands.log"
            $logEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] BLOCKED: $Command | Reason: $Reason"
            Add-Content -Path $logFile -Value $logEntry
        }
        catch {
            # Silently ignore logging errors
        }
    }

    $result | ConvertTo-Json -Compress | Write-Output
}

# Load configuration
try {
    if (-not (Test-Path $configPath)) {
        # No config file - allow by default (fail open)
        Write-Decision -Decision "allow" -Reason "No config file found - allowing by default"
        exit 0
    }
    $config = Get-Content $configPath -Raw | ConvertFrom-Json
}
catch {
    # Config parse error - ask user to be safe
    Write-Decision -Decision "ask" -Reason "Failed to parse config: $_"
    exit 0
}

# Parse input
try {
    $input = $InputJson | ConvertFrom-Json
}
catch {
    Write-Decision -Decision "ask" -Reason "Failed to parse input JSON"
    exit 0
}

# Only check shell/bash tool calls
$shellTools = @(
    "shell",
    "bash",
    "execute_command",
    "run_terminal_command",
    "run_command",
    "terminal",
    "cmd"
)

if ($input.tool -notin $shellTools) {
    # Not a shell tool - allow
    Write-Decision -Decision "allow" -Reason "Non-shell tool"
    exit 0
}

# Extract command from various possible parameter names
$command = $null
if ($input.parameters.command) {
    $command = $input.parameters.command
}
elseif ($input.parameters.cmd) {
    $command = $input.parameters.cmd
}
elseif ($input.parameters.script) {
    $command = $input.parameters.script
}
elseif ($input.parameters.code) {
    $command = $input.parameters.code
}

if (-not $command) {
    Write-Decision -Decision "ask" -Reason "Could not extract command from parameters"
    exit 0
}

# Normalize command (trim whitespace, collapse multiple spaces)
$command = $command.Trim() -replace '\s+', ' '

# Check blocked patterns first (deny takes precedence)
foreach ($rule in $config.blocked_patterns) {
    try {
        if ($command -match $rule.pattern) {
            $reason = if ($rule.reason) { $rule.reason } else { "Matches blocked pattern: $($rule.pattern)" }
            $severity = if ($rule.severity) { "[$($rule.severity.ToUpper())] " } else { "" }
            Write-Decision -Decision "block" -Reason "${severity}${reason}" -Command $command
            exit 0
        }
    }
    catch {
        # Invalid regex - skip this pattern
        continue
    }
}

# Check allowed patterns
foreach ($rule in $config.allowed_patterns) {
    try {
        if ($command -match $rule.pattern) {
            Write-Decision -Decision "allow" -Reason $rule.reason
            exit 0
        }
    }
    catch {
        # Invalid regex - skip this pattern
        continue
    }
}

# No match - use default action
$defaultAction = if ($config.default_action) { $config.default_action } else { "ask" }
Write-Decision -Decision $defaultAction -Reason "Command not in allow/block list - requires approval: $command"
