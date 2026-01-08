$ErrorActionPreference = "Stop"
$WorkspaceRoot = $env:GEMINI_PROJECT_DIR
if (-not $WorkspaceRoot) { $WorkspaceRoot = Get-Location }
$PanicFile = Join-Path $WorkspaceRoot ".panic"

if (Test-Path $PanicFile) {
    Write-Output '{"decision": "block", "reason": "PANIC MODE ACTIVE"}'
    exit 2
}

$Context = "Constitutional constraints are active. CONST-001: Human supremacy. CONST-002: Panic halt. CONST-003: Single ownership. CONST-004: No code execution. CONST-005: Explicit prohibition."
$JsonPayload = @{
    decision = "allow"
    additionalContext = $Context
}
Write-Output ($JsonPayload | ConvertTo-Json -Compress)
exit 0
