<#
.SYNOPSIS
    Wiggum - Autonomous Agent Loop for Gemini CLI

.DESCRIPTION
    PowerShell wrapper for running Wiggum autonomous development loop.
    This script provides an easy-to-use interface for the Python-based Wiggum system.

.PARAMETER Spec
    Path to the feature specification markdown file.

.PARAMETER PlanOnly
    Only generate plan, don't execute.

.PARAMETER DryRun
    Don't actually write files.

.PARAMETER Verbose
    Enable verbose output.

.PARAMETER NoReview
    Skip the review phase.

.PARAMETER NoMeta
    Skip the meta check phase.

.PARAMETER MaxSteps
    Maximum steps to execute (default: 50).

.PARAMETER MaxTime
    Maximum runtime in seconds (default: 3600).

.PARAMETER Output
    Output file for results (JSON).

.EXAMPLE
    .\.gemini\wiggum.ps1 -Spec specs/new-feature.md

.EXAMPLE
    .\.gemini\wiggum.ps1 -Spec specs/new-feature.md -PlanOnly

.EXAMPLE
    .\.gemini\wiggum.ps1 -Spec specs/new-feature.md -DryRun -Verbose
#>

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Spec,

    [switch]$PlanOnly,
    [switch]$DryRun,
    [switch]$Verbose,
    [switch]$NoReview,
    [switch]$NoMeta,

    [int]$MaxSteps = 50,
    [int]$MaxTime = 3600,

    [string]$Output
)

# Check for GEMINI_API_KEY
if (-not $env:GEMINI_API_KEY) {
    Write-Host "ERROR: GEMINI_API_KEY environment variable not set." -ForegroundColor Red
    Write-Host ""
    Write-Host "Set it with:"
    Write-Host '  $env:GEMINI_API_KEY = "your-api-key"'
    Write-Host ""
    exit 1
}

# Check for Python
$pythonCmd = $null
foreach ($cmd in @("python3", "python", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python 3") {
            $pythonCmd = $cmd
            break
        }
    }
    catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "ERROR: Python 3 not found." -ForegroundColor Red
    Write-Host "Please install Python 3.8 or later."
    exit 1
}

# Check for required packages
$checkPackages = & $pythonCmd -c "import google.generativeai; import yaml" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    & $pythonCmd -m pip install google-generativeai pyyaml --quiet
}

# Build arguments
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$wiggumModule = Join-Path $scriptDir "wiggum"

$args = @(
    "-m", "wiggum",
    "--spec", $Spec,
    "--max-steps", $MaxSteps,
    "--max-time", $MaxTime
)

if ($PlanOnly) { $args += "--plan-only" }
if ($DryRun) { $args += "--dry-run" }
if ($Verbose) { $args += "--verbose" }
if ($NoReview) { $args += "--no-review" }
if ($NoMeta) { $args += "--no-meta" }
if ($Output) { $args += @("--output", $Output) }

# Set PYTHONPATH to include .gemini directory
$env:PYTHONPATH = $scriptDir

# Run Wiggum
Write-Host ""
Write-Host "Starting Wiggum..." -ForegroundColor Cyan
Write-Host ""

Push-Location $scriptDir
try {
    & $pythonCmd $args
    $exitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

exit $exitCode
