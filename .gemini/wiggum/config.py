#!/usr/bin/env python3
"""
Configuration management for Wiggum.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json


def load_dotenv_file(env_path: Optional[Path] = None):
    """
    Load environment variables from .env file.

    Searches in order:
    1. Provided path
    2. .gemini/.env
    3. Project root .env
    """
    search_paths = []

    if env_path:
        search_paths.append(Path(env_path))

    # Add default paths
    gemini_root = Path(__file__).parent.parent
    search_paths.extend([
        gemini_root / ".env",
        gemini_root.parent / ".env",
    ])

    for path in search_paths:
        if path.exists():
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        # Only set if not already set (env vars take precedence)
                        if key not in os.environ:
                            os.environ[key] = value
            return True

    return False


# Auto-load .env on module import
load_dotenv_file()


@dataclass
class WiggumConfig:
    """Configuration for Wiggum autonomous agent loop."""

    # API Configuration
    api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    model_name: str = "gemini-2.0-flash"  # Best balance of speed and capability
    planning_model: str = "gemini-2.0-flash"  # Can use different model for planning

    # Rate Limiting
    max_calls_per_hour: int = 100
    max_calls_per_minute: int = 10
    cooldown_seconds: int = 60

    # Circuit Breaker
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    max_consecutive_failures: int = 5
    failure_reset_seconds: int = 300

    # Execution Limits
    max_steps: int = 50  # Maximum steps in a single run
    max_runtime_seconds: int = 3600  # 1 hour max runtime
    max_file_size_bytes: int = 1_000_000  # 1MB max file size

    # Paths (relative to .gemini folder)
    workspace_root: Path = field(default_factory=lambda: Path.cwd())
    gemini_root: Path = field(default_factory=lambda: Path.cwd() / ".gemini")
    logs_dir: Path = field(default_factory=lambda: Path.cwd() / ".gemini" / "logs")

    # Feature Flags
    dry_run: bool = False  # If True, don't actually write files
    verbose: bool = False
    enable_review: bool = True
    enable_meta_check: bool = True
    enable_monitoring: bool = True

    # Safety
    blocked_paths: list = field(default_factory=lambda: [
        ".git",
        "node_modules",
        ".env",
        "*.pem",
        "*.key",
        "**/secrets/**",
        "**/credentials/**"
    ])

    allowed_extensions: list = field(default_factory=lambda: [
        ".cs", ".csx",  # C#
        ".ts", ".tsx", ".js", ".jsx",  # TypeScript/JavaScript
        ".json", ".yaml", ".yml", ".toml",  # Config
        ".md", ".txt",  # Documentation
        ".html", ".css", ".scss",  # Web
        ".sql",  # Database
        ".sh", ".ps1", ".bat",  # Scripts
        ".xml", ".config",  # .NET config
        ".csproj", ".sln",  # .NET projects
    ])

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        # Ensure paths are Path objects
        if isinstance(self.workspace_root, str):
            self.workspace_root = Path(self.workspace_root)
        if isinstance(self.gemini_root, str):
            self.gemini_root = Path(self.gemini_root)
        if isinstance(self.logs_dir, str):
            self.logs_dir = Path(self.logs_dir)

    @classmethod
    def from_file(cls, config_path: Path) -> "WiggumConfig":
        """Load configuration from a JSON file."""
        if not config_path.exists():
            return cls()

        with open(config_path) as f:
            data = json.load(f)

        return cls(**data)

    @classmethod
    def from_env(cls) -> "WiggumConfig":
        """Create configuration from environment variables."""
        return cls(
            api_key=os.getenv("GEMINI_API_KEY", ""),
            model_name=os.getenv("WIGGUM_MODEL", "gemini-2.0-flash"),
            max_calls_per_hour=int(os.getenv("WIGGUM_RATE_LIMIT", "100")),
            max_steps=int(os.getenv("WIGGUM_MAX_STEPS", "50")),
            dry_run=os.getenv("WIGGUM_DRY_RUN", "").lower() == "true",
            verbose=os.getenv("WIGGUM_VERBOSE", "").lower() == "true",
        )

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "model_name": self.model_name,
            "max_calls_per_hour": self.max_calls_per_hour,
            "max_steps": self.max_steps,
            "dry_run": self.dry_run,
            "verbose": self.verbose,
            "enable_review": self.enable_review,
            "enable_meta_check": self.enable_meta_check,
        }
