$ErrorActionPreference = "Stop"

# Load smart path resolver
. "$PSScriptRoot/../../lib/paths.ps1"

$RootPath = $Paths.Workspace
$MapFile = $Paths.Files.Architecture

# --- Performance & Exclusions ---
# Smart Exclude: Skip heavy/irrelevant folders to reduce IO and Token noise
$ExcludeRegex = "[\\/](bin|obj|node_modules|dist|build|coverage|\.git|\.vs|\.vscode|test-results|assets|public|wwwroot|mocks|__tests__)[\\/]"

$Header = @"
# Architecture Map (Structural Memory)
*Auto-Generated: $(Get-Date)*

## Purpose
High-level dependency graph of the user code.

## Modules
"@

$Content = @()
$Content += $Header

# --- Helper: Fast Export Extraction (Uses Select-String) ---
function Get-TSExports {
    param ($FilePath)
    # Fast native grep for 'export class/const/etc X'
    $Matches = Select-String -Path $FilePath -Pattern 'export\s+(?:const|function|class|type|interface|enum)\s+(\w+)'
    if ($Matches) {
        return ($Matches.Matches.Groups[1].Value | Select-Object -Unique) -join ", "
    }
    return $null
}

# --- C# Projects ---
$CsProjects = Get-ChildItem -Path $RootPath -Filter *.csproj -Recurse | Where-Object { $_.FullName -notmatch $ExcludeRegex }
if ($CsProjects) {
    foreach ($Proj in $CsProjects) {
        $Content += "`n### Project (C#): $($Proj.Name)"
        
        $Files = Get-ChildItem -Path $Proj.Directory -Filter *.cs -Recurse | Where-Object { $_.FullName -notmatch $ExcludeRegex }
        foreach ($File in $Files) {
            # OPTIMIZATION: Read only first 50 lines for namespace (avoids reading full file)
            $HeadLines = Get-Content $File.FullName -TotalCount 50
            $NamespaceMatch = $HeadLines | Select-String -Pattern 'namespace\s+([\w\.]+)' | Select-Object -First 1
            
            if ($NamespaceMatch) {
                $Ns = $NamespaceMatch.Matches.Groups[1].Value
                $Content += "*   **$($File.Name)** ($Ns)"
            } else {
                $Content += "*   **$($File.Name)**"
            }
        }
    }
}

# --- Node/TS Projects ---
# Find folders with package.json, ignoring excludes
$NodeProjects = Get-ChildItem -Path $RootPath -Filter package.json -Recurse | Where-Object { $_.FullName -notmatch $ExcludeRegex }

if ($NodeProjects) {
    foreach ($Pkg in $NodeProjects) {
        try {
            $ProjName = (Get-Content $Pkg.FullName -Raw | ConvertFrom-Json).name
        } catch {
            $ProjName = $Pkg.Directory.Name 
        }
        if (-not $ProjName) { $ProjName = $Pkg.Directory.Name }
        
        $Content += "`n### Project (TS/JS): $ProjName"
        
        # Scan for TS/TSX files
        $Files = Get-ChildItem -Path $Pkg.Directory -Include *.ts,*.tsx -Recurse | Where-Object { $_.FullName -notmatch $ExcludeRegex }
        
        foreach ($File in $Files) {
            $Exports = Get-TSExports -FilePath $File.FullName
            if ($Exports) {
                $Content += "*   **$($File.Name)** (Exports: $Exports)"
            } else {
                $Content += "*   **$($File.Name)**"
            }
        }
    }
}

$Content | Set-Content $MapFile
Write-Host "Map updated at $MapFile"
