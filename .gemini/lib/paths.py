#!/usr/bin/env python3
"""
Smart Path Resolver for Python scripts.

Supports multiple environments:
- Local development (relative paths)
- CI/CD pipelines (environment variables)
- Docker containers (mounted volumes)

Environment Variables (all optional):
- WORKSPACE_ROOT: Override workspace root directory
- GEMINI_DIR: Override .gemini directory location
- GEMMEM_DIR: Override .gemmem directory location
- GEMINI_PROJECT_DIR: Legacy support (Gemini CLI)

Usage:
    from lib.paths import paths
    print(paths.workspace)    # /app or C:\\Projects\\ai-platform
    print(paths.gemmem)       # /app/.gemmem
    print(paths.gemini)       # /app/.gemini
    print(paths.resolve('src/index.ts'))  # Full path to file
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


def _detect_workspace_root(start_dir: Path) -> Path:
    """
    Detect workspace root by searching for marker files/folders.
    Walks up from start_dir until it finds a workspace marker.
    """
    current = start_dir.resolve()

    while current != current.parent:
        # Check for .gemini folder (strongest indicator)
        if (current / '.gemini').exists():
            return current

        # Check for .git folder
        if (current / '.git').exists():
            return current

        # Check for solution file (Windows .NET projects)
        if any(current.glob('*.sln')):
            return current

        current = current.parent

    # Fallback: return start directory
    return start_dir


def _resolve_workspace() -> Path:
    """
    Resolve the workspace root directory.
    Priority: ENV > Detection > Fallback
    """
    # 1. Check explicit environment variable
    if os.environ.get('WORKSPACE_ROOT'):
        return Path(os.environ['WORKSPACE_ROOT']).resolve()

    # 2. Check Gemini CLI environment variable (legacy support)
    if os.environ.get('GEMINI_PROJECT_DIR'):
        return Path(os.environ['GEMINI_PROJECT_DIR']).resolve()

    # 3. Check GitHub Actions workspace
    if os.environ.get('GITHUB_WORKSPACE'):
        return Path(os.environ['GITHUB_WORKSPACE']).resolve()

    # 4. Check Azure DevOps workspace
    if os.environ.get('BUILD_SOURCESDIRECTORY'):
        return Path(os.environ['BUILD_SOURCESDIRECTORY']).resolve()

    # 5. Check GitLab CI workspace
    if os.environ.get('CI_PROJECT_DIR'):
        return Path(os.environ['CI_PROJECT_DIR']).resolve()

    # 6. Auto-detect from current file location
    # __file__ is .gemini/lib/paths.py, so workspace is ../../
    script_dir = Path(__file__).parent
    detected = _detect_workspace_root(script_dir)

    if detected != script_dir:
        return detected

    # 7. Fallback: two levels up from this script
    return (script_dir / '../..').resolve()


def _resolve_gemini_dir(workspace: Path) -> Path:
    """Resolve the .gemini directory."""
    if os.environ.get('GEMINI_DIR'):
        return Path(os.environ['GEMINI_DIR']).resolve()
    return workspace / '.gemini'


def _resolve_gemmem_dir(workspace: Path) -> Path:
    """Resolve the .gemmem directory (architecture & lessons)."""
    if os.environ.get('GEMMEM_DIR'):
        return Path(os.environ['GEMMEM_DIR']).resolve()
    return workspace / '.gemmem'


@dataclass(frozen=True)
class PathFiles:
    """Key file paths."""
    architecture: Path
    lessons: Path
    rules: Path
    compiled_rules: Path
    hooks: Path
    tools: Path
    logs: Path


class Paths:
    """Smart path resolver for the AI Platform project."""

    def __init__(self):
        self._workspace = _resolve_workspace()
        self._gemini = _resolve_gemini_dir(self._workspace)
        self._gemmem = _resolve_gemmem_dir(self._workspace)

        self._files = PathFiles(
            architecture=self._gemmem / 'ARCHITECTURE.md',
            lessons=self._gemmem / 'LESSONS.md',
            rules=self._gemini / 'rules',
            compiled_rules=self._gemini / 'rules' / 'compiled',
            hooks=self._gemini / 'hooks',
            tools=self._gemini / 'tools',
            logs=self._gemini / 'logs',
        )

    @property
    def workspace(self) -> Path:
        """Workspace root directory."""
        return self._workspace

    @property
    def gemini(self) -> Path:
        """.gemini directory (OS configuration)."""
        return self._gemini

    @property
    def gemmem(self) -> Path:
        """.gemmem directory (architecture & lessons)."""
        return self._gemmem

    @property
    def files(self) -> PathFiles:
        """Key file paths."""
        return self._files

    def resolve(self, relative_path: str) -> Path:
        """
        Resolve a path relative to workspace root.

        Args:
            relative_path: Path relative to workspace

        Returns:
            Absolute path
        """
        return self._workspace / relative_path

    def resolve_gemini(self, relative_path: str) -> Path:
        """
        Resolve a path relative to .gemini directory.

        Args:
            relative_path: Path relative to .gemini

        Returns:
            Absolute path
        """
        return self._gemini / relative_path

    def resolve_gemmem(self, relative_path: str) -> Path:
        """
        Resolve a path relative to .gemmem directory.

        Args:
            relative_path: Path relative to .gemmem

        Returns:
            Absolute path
        """
        return self._gemmem / relative_path

    def is_ci(self) -> bool:
        """Check if running in CI environment."""
        return bool(
            os.environ.get('CI') or
            os.environ.get('GITHUB_ACTIONS') or
            os.environ.get('TF_BUILD') or
            os.environ.get('GITLAB_CI') or
            os.environ.get('JENKINS_URL')
        )

    def is_docker(self) -> bool:
        """Check if running in Docker container."""
        try:
            # Check for .dockerenv file
            if Path('/.dockerenv').exists():
                return True

            # Check cgroup for docker
            cgroup_path = Path('/proc/1/cgroup')
            if cgroup_path.exists():
                return 'docker' in cgroup_path.read_text()
        except Exception:
            pass

        return False

    def get_environment_info(self) -> dict:
        """Get environment info for debugging."""
        return {
            'workspace': str(self._workspace),
            'gemini': str(self._gemini),
            'gemmem': str(self._gemmem),
            'is_ci': self.is_ci(),
            'is_docker': self.is_docker(),
            'platform': os.name,
            'env': {
                'WORKSPACE_ROOT': os.environ.get('WORKSPACE_ROOT', '(not set)'),
                'GEMINI_PROJECT_DIR': os.environ.get('GEMINI_PROJECT_DIR', '(not set)'),
                'GEMINI_DIR': os.environ.get('GEMINI_DIR', '(not set)'),
                'GEMMEM_DIR': os.environ.get('GEMMEM_DIR', '(not set)'),
            }
        }


# Singleton instance
paths = Paths()


# Convenience exports for direct access
workspace = paths.workspace
gemini = paths.gemini
gemmem = paths.gemmem
files = paths.files
resolve = paths.resolve
resolve_gemini = paths.resolve_gemini
resolve_gemmem = paths.resolve_gemmem
is_ci = paths.is_ci
is_docker = paths.is_docker


if __name__ == '__main__':
    import json
    print(json.dumps(paths.get_environment_info(), indent=2))
