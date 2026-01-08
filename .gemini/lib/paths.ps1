<#
.SYNOPSIS
    Smart Path Resolver for PowerShell scripts.

.DESCRIPTION
    Supports multiple environments:
    - Local development (relative paths)
    - CI/CD pipelines (environment variables)
    - Docker containers (mounted volumes)

    Environment Variables (all optional):
    - WORKSPACE_ROOT: Override workspace root directory
    - GEMINI_DIR: Override .gemini directory location
    - GEMMEM_DIR: Override .gemmem directory location
    - GEMINI_PROJECT_DIR: Legacy support (Gemini CLI)

.EXAMPLE
    . "$PSScriptRoot/../lib/paths.ps1"
    Write-Host $Paths.Workspace
    Write-Host $Paths.Gemmem
    Write-Host (Resolve-WorkspacePath "src/index.ts")
#>

function Find-WorkspaceRoot {
    param (
        [string]$StartDir
    )

    $Current = (Resolve-Path $StartDir -ErrorAction SilentlyContinue).Path
    if (-not $Current) { $Current = $StartDir }

    while ($Current) {
        # Check for .gemini folder (strongest indicator)
        if (Test-Path (Join-Path $Current ".gemini")) {
            return $Current
        }

        # Check for .git folder
        if (Test-Path (Join-Path $Current ".git")) {
            return $Current
        }

        # Check for solution file (.sln)
        if (Get-ChildItem -Path $Current -Filter "*.sln" -ErrorAction SilentlyContinue) {
            return $Current
        }

        $Parent = Split-Path $Current -Parent
        if ($Parent -eq $Current) { break }
        $Current = $Parent
    }

    return $StartDir
}

function Get-WorkspaceRoot {
    # 1. Check explicit environment variable
    if ($env:WORKSPACE_ROOT) {
        return (Resolve-Path $env:WORKSPACE_ROOT).Path
    }

    # 2. Check Gemini CLI environment variable (legacy support)
    if ($env:GEMINI_PROJECT_DIR) {
        return (Resolve-Path $env:GEMINI_PROJECT_DIR).Path
    }

    # 3. Check GitHub Actions workspace
    if ($env:GITHUB_WORKSPACE) {
        return (Resolve-Path $env:GITHUB_WORKSPACE).Path
    }

    # 4. Check Azure DevOps workspace
    if ($env:BUILD_SOURCESDIRECTORY) {
        return (Resolve-Path $env:BUILD_SOURCESDIRECTORY).Path
    }

    # 5. Check GitLab CI workspace
    if ($env:CI_PROJECT_DIR) {
        return (Resolve-Path $env:CI_PROJECT_DIR).Path
    }

    # 6. Auto-detect from current script location
    # This script is at .gemini/lib/paths.ps1, so workspace is ../../
    $ScriptDir = $PSScriptRoot
    if (-not $ScriptDir) {
        $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    }

    $Detected = Find-WorkspaceRoot -StartDir $ScriptDir
    if ($Detected -ne $ScriptDir) {
        return $Detected
    }

    # 7. Fallback: two levels up from this script
    return (Resolve-Path (Join-Path $ScriptDir "../../")).Path
}

function Get-GeminiDir {
    param ([string]$Workspace)

    if ($env:GEMINI_DIR) {
        return (Resolve-Path $env:GEMINI_DIR).Path
    }
    return Join-Path $Workspace ".gemini"
}

function Get-GemmemDir {
    param ([string]$Workspace)

    if ($env:GEMMEM_DIR) {
        return (Resolve-Path $env:GEMMEM_DIR).Path
    }
    return Join-Path $Workspace ".gemmem"
}

function Test-IsCI {
    return (
        $env:CI -or
        $env:GITHUB_ACTIONS -or
        $env:TF_BUILD -or
        $env:GITLAB_CI -or
        $env:JENKINS_URL
    )
}

function Test-IsDocker {
    # Check for .dockerenv file
    if (Test-Path "/.dockerenv") { return $true }

    # Check cgroup for docker (Linux)
    try {
        if (Test-Path "/proc/1/cgroup") {
            $Content = Get-Content "/proc/1/cgroup" -Raw
            if ($Content -match "docker") { return $true }
        }
    } catch {}

    return $false
}

# Resolve paths once at module load
$WorkspaceRoot = Get-WorkspaceRoot
$GeminiDir = Get-GeminiDir -Workspace $WorkspaceRoot
$GemmemDir = Get-GemmemDir -Workspace $WorkspaceRoot

# Export paths object
$script:Paths = @{
    Workspace = $WorkspaceRoot
    Gemini = $GeminiDir
    Gemmem = $GemmemDir

    Files = @{
        Architecture = Join-Path $GemmemDir "ARCHITECTURE.md"
        Lessons = Join-Path $GemmemDir "LESSONS.md"
        Rules = Join-Path $GeminiDir "rules"
        CompiledRules = Join-Path $GeminiDir "rules/compiled"
        Hooks = Join-Path $GeminiDir "hooks"
        Tools = Join-Path $GeminiDir "tools"
        Logs = Join-Path $GeminiDir "logs"
    }

    IsCI = Test-IsCI
    IsDocker = Test-IsDocker
}

function Resolve-WorkspacePath {
    param ([string]$RelativePath)
    return Join-Path $script:Paths.Workspace $RelativePath
}

function Resolve-GeminiPath {
    param ([string]$RelativePath)
    return Join-Path $script:Paths.Gemini $RelativePath
}

function Resolve-GemmemPath {
    param ([string]$RelativePath)
    return Join-Path $script:Paths.Gemmem $RelativePath
}

function Get-PathsEnvironmentInfo {
    return @{
        Workspace = $script:Paths.Workspace
        Gemini = $script:Paths.Gemini
        Gemmem = $script:Paths.Gemmem
        IsCI = $script:Paths.IsCI
        IsDocker = $script:Paths.IsDocker
        Platform = $PSVersionTable.Platform
        Env = @{
            WORKSPACE_ROOT = if ($env:WORKSPACE_ROOT) { $env:WORKSPACE_ROOT } else { "(not set)" }
            GEMINI_PROJECT_DIR = if ($env:GEMINI_PROJECT_DIR) { $env:GEMINI_PROJECT_DIR } else { "(not set)" }
            GEMINI_DIR = if ($env:GEMINI_DIR) { $env:GEMINI_DIR } else { "(not set)" }
            GEMMEM_DIR = if ($env:GEMMEM_DIR) { $env:GEMMEM_DIR } else { "(not set)" }
        }
    }
}

# Export module members
Export-ModuleMember -Variable Paths -Function @(
    'Resolve-WorkspacePath',
    'Resolve-GeminiPath',
    'Resolve-GemmemPath',
    'Get-PathsEnvironmentInfo',
    'Test-IsCI',
    'Test-IsDocker'
)
