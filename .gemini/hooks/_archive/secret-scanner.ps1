# .gemini/hooks/secret-scanner.ps1
# Scans for potential secrets (API keys, JWTs, etc.) before they are written to disk.

# Common patterns for secrets
$Patterns = @(
    "(?i)eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*", # JWT
    "sk-[a-zA-Z0-9]{20,}",                                          # Generic secret keys
    "AIza[0-9A-Za-z-_]{35}",                                        # Google API Key
    "-[0-9a-zA-Z]{32}",                                             # Generic 32-char keys
    "connectionString":\s*"[^"]*Password=[^"]*"
)

# Note: In a real hook, the CLI would pass the content to scan via stdin or a temp file.
# For this implementation, we scan the current staged changes or the last modified file in the workspace
# as a safety net.

$TargetFiles = git diff --name-only --cached
if (-not $TargetFiles) {
    $TargetFiles = Get-ChildItem -Path . -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 5 -ExpandProperty FullName
}

foreach ($File in $TargetFiles) {
    if (Test-Path $File -PathType Leaf) {
        $Content = Get-Content $File -Raw
        foreach ($Pattern in $Patterns) {
            if ($Content -match $Pattern) {
                Write-Host "🛑 SECURITY ALERT: Potential secret detected in $File" -ForegroundColor Red
                Write-Host "Pattern matched: $Pattern" -ForegroundColor Red
                Write-Host "Operation blocked by Corporate Security Policy." -ForegroundColor Red
                exit 1
            }
        }
    }
}

exit 0
