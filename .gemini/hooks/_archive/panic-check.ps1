$ErrorActionPreference = "Stop"
$WorkspaceRoot = $env:GEMINI_PROJECT_DIR
if (-not $WorkspaceRoot) { $WorkspaceRoot = Get-Location }
$PanicFile = Join-Path $WorkspaceRoot ".panic"

if (Test-Path $PanicFile) {
    Write-Output '{"decision": "block", "reason": "PANIC MODE ACTIVE: .panic file detected. All operations halted. Human intervention required."}'
    exit 2
}

Write-Output '{"decision": "allow"}'
exit 0
