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
- GEMINI_PROJECT_DIR: Legacy support (Gemini CLI)
"""

import os
from pathlib import Path
from dataclasses import dataclass


def _detect_workspace_root(start_dir: Path) -> Path:
    """Detect workspace root by searching for marker files/folders."""
    current = start_dir.resolve()

    while current != current.parent:
        if (current / '.gemini').exists():
            return current
        if (current / '.git').exists():
            return current
        if any(current.glob('*.sln')):
            return current
        current = current.parent

    return start_dir


def _resolve_workspace() -> Path:
    """Resolve the workspace root directory."""
    if os.environ.get('WORKSPACE_ROOT'):
        return Path(os.environ['WORKSPACE_ROOT']).resolve()
    if os.environ.get('GEMINI_PROJECT_DIR'):
        return Path(os.environ['GEMINI_PROJECT_DIR']).resolve()
    if os.environ.get('GITHUB_WORKSPACE'):
        return Path(os.environ['GITHUB_WORKSPACE']).resolve()
    if os.environ.get('BUILD_SOURCESDIRECTORY'):
        return Path(os.environ['BUILD_SOURCESDIRECTORY']).resolve()
    if os.environ.get('CI_PROJECT_DIR'):
        return Path(os.environ['CI_PROJECT_DIR']).resolve()

    script_dir = Path(__file__).parent
    detected = _detect_workspace_root(script_dir)
    return detected if detected != script_dir else (script_dir / '../..').resolve()


def _resolve_gemini_dir(workspace: Path) -> Path:
    """Resolve the .gemini directory."""
    if os.environ.get('GEMINI_DIR'):
        return Path(os.environ['GEMINI_DIR']).resolve()
    return workspace / '.gemini'


@dataclass(frozen=True)
class PathFiles:
    """Key file paths."""
    rules: Path
    compiled_rules: Path
    hooks: Path
    skills: Path


class Paths:
    """Smart path resolver for the AI Platform project."""

    def __init__(self):
        self._workspace = _resolve_workspace()
        self._gemini = _resolve_gemini_dir(self._workspace)

        self._files = PathFiles(
            rules=self._gemini / 'knowledge',
            compiled_rules=self._gemini / 'knowledge' / 'compiled',
            hooks=self._gemini / 'hooks',
            skills=self._gemini / 'skills',
        )

    @property
    def workspace(self) -> Path:
        """Workspace root directory."""
        return self._workspace

    @property
    def gemini(self) -> Path:
        """.gemini directory."""
        return self._gemini

    @property
    def files(self) -> PathFiles:
        """Key file paths."""
        return self._files

    def resolve(self, relative_path: str) -> Path:
        """Resolve a path relative to workspace root."""
        return self._workspace / relative_path

    def resolve_gemini(self, relative_path: str) -> Path:
        """Resolve a path relative to .gemini directory."""
        return self._gemini / relative_path

    def is_ci(self) -> bool:
        """Check if running in CI environment."""
        return bool(
            os.environ.get('CI') or
            os.environ.get('GITHUB_ACTIONS') or
            os.environ.get('TF_BUILD') or
            os.environ.get('GITLAB_CI') or
            os.environ.get('JENKINS_URL')
        )

    def get_environment_info(self) -> dict:
        """Get environment info for debugging."""
        return {
            'workspace': str(self._workspace),
            'gemini': str(self._gemini),
            'is_ci': self.is_ci(),
            'platform': os.name,
        }


# Singleton instance
paths = Paths()

# Convenience exports
workspace = paths.workspace
gemini = paths.gemini
files = paths.files
resolve = paths.resolve
resolve_gemini = paths.resolve_gemini
is_ci = paths.is_ci


if __name__ == '__main__':
    import json
    print(json.dumps(paths.get_environment_info(), indent=2))
