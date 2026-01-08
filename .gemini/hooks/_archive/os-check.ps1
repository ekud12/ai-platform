# .gemini/hooks/os-check.ps1
# Checks if the local .gemini configuration is up to date with the remote repository.

$ErrorActionPreference = "SilentlyContinue"

Write-Host "[OS-CHECK] Checking for AI OS updates..." -ForegroundColor Cyan

# Check if we are in a git repo
git rev-parse --is-inside-work-tree > $null
if ($LASTEXITCODE -ne 0) { return }

# Fetch status of the .gemini directory
git fetch origin main > $null

$LocalHash = git rev-parse HEAD:.gemini
$RemoteHash = git rev-parse origin/main:.gemini

if ($LocalHash -ne $RemoteHash) {
    Write-Host "⚠️  WARNING: Your local AI OS (.gemini folder) is out of sync with the team standards." -ForegroundColor Yellow
    Write-Host "Please run 'git pull' or 'git submodule update' to ensure development consistency." -ForegroundColor Yellow
} else {
    Write-Host "✅ AI OS is up to date." -ForegroundColor Green
}
