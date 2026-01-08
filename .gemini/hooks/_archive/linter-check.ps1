# .gemini/hooks/linter-check.ps1
# Runs official linters (dotnet format, eslint) on changed files.
# This ensures code complies with the project's .editorconfig and .eslintrc.

$ErrorActionPreference = "SilentlyContinue"
$ExitCode = 0

Write-Host "[LINTER] Verifying compliance with official project standards..." -ForegroundColor Cyan

# 1. Get Changed Files
$ChangedFiles = git diff --name-only --cached
if (-not $ChangedFiles) {
    # If nothing staged, checking recent workspace changes could be slow, so we skip or check specific files
    # For this hook, we'll assume we want to check STAGED files before commit, or specific files if passed as args.
    exit 0
}

# 2. Check .NET Files
$DotNetFiles = $ChangedFiles | Where-Object { $_ -match "\.cs$" }
if ($DotNetFiles) {
    # Run dotnet format in verify mode (doesn't fix, just yells)
    # This reads .editorconfig, which IS the official documentation for the project style.
    Write-Host "   Checking C# styles..." -NoNewline
    dotnet format whitespace --verify-no-changes --include $DotNetFiles > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host " [FAIL]" -ForegroundColor Red
        Write-Host "   ❌ C# files violate .editorconfig standards. Run 'dotnet format' to fix." -ForegroundColor Yellow
        $ExitCode = 1
    } else {
        Write-Host " [PASS]" -ForegroundColor Green
    }
}

# 3. Check TypeScript/JS Files
$TSFiles = $ChangedFiles | Where-Object { $_ -match "\.(ts|tsx|js|jsx)$" }
if ($TSFiles) {
    Write-Host "   Checking TS styles..." -NoNewline
    # Assumes 'lint' script exists in package.json. If not, this skips.
    npm run lint --silent > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host " [FAIL]" -ForegroundColor Red
        Write-Host "   ❌ TypeScript files violate eslint rules." -ForegroundColor Yellow
        $ExitCode = 1
    } else {
        Write-Host " [PASS]" -ForegroundColor Green
    }
}

if ($ExitCode -ne 0) {
    Write-Host "🛑 BLOCK: Code does not meet official standards." -ForegroundColor Red
    exit 1
}

exit 0
