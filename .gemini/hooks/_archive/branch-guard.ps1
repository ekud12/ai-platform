# .gemini/hooks/branch-guard.ps1
# Prevents agents from modifying code on protected branches.

$ProtectedBranches = @("main", "master", "production", "release", "demo", "develop")

# Get current branch
$CurrentBranch = git rev-parse --abbrev-ref HEAD 2>$null

if (-not $CurrentBranch) {
    # Not a git repo, skip
    exit 0
}

if ($ProtectedBranches -contains $CurrentBranch) {
    Write-Host "🛑 BRANCH PROTECTION: You are on '$CurrentBranch'." -ForegroundColor Red
    Write-Host "Direct modifications to protected branches are forbidden." -ForegroundColor Red
    Write-Host "Please create a feature branch: git checkout -b feature/your-task" -ForegroundColor Yellow
    exit 1
}

exit 0
