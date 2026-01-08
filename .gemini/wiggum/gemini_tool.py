#!/usr/bin/env python3
"""
Gemini CLI Tool Integration for Wiggum.

This module provides a function that can be called directly from within
a Gemini CLI session to run Wiggum without leaving the chat.

Usage in Gemini CLI:
    Ask Gemini to: "Run wiggum on specs/feature.md"
    Gemini can then execute this tool.
"""

import sys
import json
from pathlib import Path
from typing import Optional


def run_wiggum_from_chat(
    spec_path: str,
    plan_only: bool = False,
    dry_run: bool = False,
    verbose: bool = False
) -> dict:
    """
    Run Wiggum from within a Gemini CLI chat session.

    This function is designed to be called by the Gemini CLI agent
    when a user requests autonomous execution.

    Args:
        spec_path: Path to the specification file
        plan_only: If True, only generate plan without executing
        dry_run: If True, don't write any files
        verbose: If True, output detailed progress

    Returns:
        Dictionary with results
    """
    # Setup paths
    script_dir = Path(__file__).parent
    gemini_root = script_dir.parent

    # Add to path
    if str(gemini_root) not in sys.path:
        sys.path.insert(0, str(gemini_root))
    if str(gemini_root / "tools") not in sys.path:
        sys.path.insert(0, str(gemini_root / "tools"))

    try:
        from wiggum.config import WiggumConfig
        from wiggum.core import Wiggum
    except ImportError as e:
        return {
            "success": False,
            "error": f"Import error: {str(e)}. Make sure google-generativeai is installed."
        }

    # Check for API key
    import os
    if not os.getenv("GEMINI_API_KEY"):
        # Try to load from .env
        env_file = gemini_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)

        if not os.getenv("GEMINI_API_KEY"):
            return {
                "success": False,
                "error": "GEMINI_API_KEY not set. Create .gemini/.env with GEMINI_API_KEY=your-key"
            }

    try:
        config = WiggumConfig(
            dry_run=dry_run,
            verbose=verbose,
        )
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }

    wiggum = Wiggum(config)

    if plan_only:
        plan = wiggum.run_plan_only(spec_path)
        if plan:
            return {
                "success": True,
                "mode": "plan_only",
                "plan": plan
            }
        else:
            return {
                "success": False,
                "error": "Failed to generate plan"
            }
    else:
        result = wiggum.run(spec_path)
        return {
            "success": result.success,
            "mode": "full_run",
            "exit_reason": result.exit_reason.value,
            "message": result.message,
            "steps_completed": result.steps_completed,
            "files_changed": result.files_changed,
            "elapsed_seconds": result.elapsed_seconds,
            "errors": result.errors
        }


def load_dotenv(env_path: Path):
    """Simple .env file loader."""
    import os

    if not env_path.exists():
        return

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value


# For direct testing
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python gemini_tool.py <spec_path> [--plan-only] [--dry-run]")
        sys.exit(1)

    spec = sys.argv[1]
    plan_only = "--plan-only" in sys.argv
    dry_run = "--dry-run" in sys.argv

    result = run_wiggum_from_chat(spec, plan_only=plan_only, dry_run=dry_run, verbose=True)
    print(json.dumps(result, indent=2))
