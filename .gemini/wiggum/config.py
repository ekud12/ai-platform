#!/usr/bin/env python3
"""
Configuration management for Wiggum.

## Wiggum vs Gemini CLI Chat Session

Wiggum is a STANDALONE autonomous agent loop that runs OUTSIDE of the Gemini CLI
chat session. It directly calls the Gemini API using the configured API key.

### Environment Variables Usage

| Variable           | Used In           | Purpose                                      |
|--------------------|-------------------|----------------------------------------------|
| GEMINI_API_KEY     | Wiggum ONLY       | API key for direct Gemini API calls          |
| WIGGUM_MODEL       | Wiggum ONLY       | Model to use (default: gemini-2.0-flash)     |
| WIGGUM_RATE_LIMIT  | Wiggum ONLY       | Max API calls per hour                       |
| WIGGUM_MAX_STEPS   | Wiggum ONLY       | Max steps in autonomous loop                 |
| WIGGUM_DRY_RUN     | Wiggum ONLY       | Preview mode without file writes             |
| WIGGUM_VERBOSE     | Wiggum ONLY       | Enable detailed logging                      |

### NOT Used in Gemini CLI Chat Session

All of the above environment variables are UNUSED in the Gemini CLI interactive
chat session. The CLI uses its own authentication and configuration:
- `.gemini/settings.json` - CLI settings (hooks, aliases, temperature)
- `.gemini/manifest.yaml` - Agent registry and rule assignments
- `.gemini/GEMINI.md` - System context and persona

### When to Use Wiggum vs CLI Chat

| Scenario                          | Tool          |
|-----------------------------------|---------------|
| Interactive development           | Gemini CLI    |
| Quick questions and fixes         | Gemini CLI    |
| Autonomous feature implementation | Wiggum        |
| Multi-step task execution         | Wiggum        |
| Spec-driven development           | Wiggum        |
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json

# Add lib directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
from paths import paths as _paths


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
    """
    Configuration for Wiggum autonomous agent loop.

    NOTE: This configuration is for the standalone Wiggum module only.
    It is NOT used by the Gemini CLI interactive chat session.

    The Gemini CLI uses:
    - Its own authentication (not GEMINI_API_KEY)
    - .gemini/settings.json for configuration
    - .gemini/manifest.yaml for agent definitions

    Environment Variables (Wiggum Only):
    ------------------------------------
    GEMINI_API_KEY      : Required. API key for Gemini API calls.
                          UNUSED in CLI chat - mark as UNUSED if only using CLI.

    WIGGUM_MODEL        : Model name (default: gemini-2.0-flash).
                          UNUSED in CLI chat.

    WIGGUM_RATE_LIMIT   : Max calls per hour (default: 100).
                          UNUSED in CLI chat.

    WIGGUM_MAX_STEPS    : Max steps per run (default: 50).
                          UNUSED in CLI chat.

    WIGGUM_DRY_RUN      : If "true", no file writes (default: false).
                          UNUSED in CLI chat.

    WIGGUM_VERBOSE      : If "true", detailed logging (default: false).
                          UNUSED in CLI chat.
    """

    # =========================================================================
    # API Configuration
    # UNUSED in Gemini CLI chat - only for standalone Wiggum execution
    # =========================================================================
    api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    model_name: str = "gemini-2.0-flash"  # Best balance of speed and capability
    planning_model: str = "gemini-2.0-flash"  # Can use different model for planning

    # =========================================================================
    # Rate Limiting
    # UNUSED in Gemini CLI chat - CLI has its own rate handling
    # =========================================================================
    max_calls_per_hour: int = 100
    max_calls_per_minute: int = 10
    cooldown_seconds: int = 60

    # =========================================================================
    # Circuit Breaker
    # UNUSED in Gemini CLI chat
    # =========================================================================
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    max_consecutive_failures: int = 5
    failure_reset_seconds: int = 300

    # =========================================================================
    # Execution Limits
    # UNUSED in Gemini CLI chat - CLI is interactive
    # =========================================================================
    max_steps: int = 50  # Maximum steps in a single run
    max_runtime_seconds: int = 3600  # 1 hour max runtime
    max_file_size_bytes: int = 1_000_000  # 1MB max file size

    # =========================================================================
    # Paths (using smart path resolver for CI/CD and Docker compatibility)
    # These are shared between Wiggum and CLI (workspace context)
    # =========================================================================
    workspace_root: Path = field(default_factory=lambda: _paths.workspace)
    gemini_root: Path = field(default_factory=lambda: _paths.gemini)
    gemmem_root: Path = field(default_factory=lambda: _paths.gemmem)
    logs_dir: Path = field(default_factory=lambda: _paths.files.logs)

    # =========================================================================
    # Feature Flags
    # UNUSED in Gemini CLI chat - these control Wiggum behavior only
    # =========================================================================
    dry_run: bool = False  # If True, don't actually write files
    verbose: bool = False
    enable_review: bool = True
    enable_meta_check: bool = True
    enable_monitoring: bool = True

    # =========================================================================
    # Safety Configuration
    # Shared concept with CLI (CLI uses .geminiignore and hooks)
    # =========================================================================
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
            raise ValueError(
                "GEMINI_API_KEY environment variable not set.\n"
                "Note: This is only required for standalone Wiggum execution.\n"
                "If you're only using the Gemini CLI chat, you can ignore this."
            )

        # Ensure paths are Path objects
        if isinstance(self.workspace_root, str):
            self.workspace_root = Path(self.workspace_root)
        if isinstance(self.gemini_root, str):
            self.gemini_root = Path(self.gemini_root)
        if isinstance(self.gemmem_root, str):
            self.gemmem_root = Path(self.gemmem_root)
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
        """
        Create configuration from environment variables.

        Environment Variables (all UNUSED in Gemini CLI chat):
        - GEMINI_API_KEY: API key for Gemini API (required for Wiggum)
        - WIGGUM_MODEL: Model name (default: gemini-2.0-flash)
        - WIGGUM_RATE_LIMIT: Max calls per hour (default: 100)
        - WIGGUM_MAX_STEPS: Max steps per run (default: 50)
        - WIGGUM_DRY_RUN: Preview mode (default: false)
        - WIGGUM_VERBOSE: Detailed logging (default: false)
        """
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
