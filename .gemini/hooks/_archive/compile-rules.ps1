<#
.SYNOPSIS
    Ensures compiled rules are up-to-date before agent execution.
.DESCRIPTION
    Runs as a BeforeAgent hook. Checks if any markdown rules are newer than
    their compiled JSON counterparts. If stale, recompiles automatically.
    Fast path: <50ms when no changes detected.
#>

$ErrorActionPreference = "Stop"
$geminiDir = Split-Path -Parent $PSScriptRoot
$toolsDir = Join-Path $geminiDir "tools"
$compileScript = Join-Path $toolsDir "compile-rules.py"

# Skip if script doesn't exist
if (-not (Test-Path $compileScript)) {
    Write-Host "compile-rules.py not found, skipping rule sync"
    exit 0
}

# Run in check mode first (fast path)
$checkResult = python $compileScript --check --quiet 2>&1
if ($LASTEXITCODE -eq 0) {
    # All rules up to date, nothing to do
    exit 0
}

# Stale rules detected, recompile
Write-Host "Compiling stale rules..."
$compileResult = python $compileScript --quiet 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Rule compilation failed: $compileResult"
    # Don't block agent execution, just warn
    exit 0
}

Write-Host "Rules compiled successfully."
exit 0
