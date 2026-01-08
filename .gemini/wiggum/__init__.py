#!/usr/bin/env python3
"""
WIGGUM - The Autonomous Agent Loop for Gemini CLI
==================================================

An enterprise-grade autonomous development system that orchestrates
specialized AI agents to plan, implement, review, and validate code changes.

Equivalent to 'Ralph' for Claude Code.

Usage:
    # From command line (headless mode)
    python -m .gemini.wiggum --spec path/to/spec.md

    # Or via shell wrapper
    ./wiggum.sh path/to/spec.md

    # From Gemini CLI (interactive)
    gemini> /wiggum path/to/spec.md

Components:
    - core.py: Main orchestration loop
    - tools.py: Gemini function calling bindings
    - agents.py: Agent loading and invocation
    - rate_limiter.py: API rate limiting
    - circuit_breaker.py: Error handling and retries
    - exit_detector.py: Task completion detection
    - config.py: Configuration management
    - rule_loader.py: JSON rule loading for structured review

Author: AI-OS Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AI-OS Team"

from .config import WiggumConfig
from .core import Wiggum
from .rule_loader import RuleLoader, load_rules_for_file, get_review_prompt

__all__ = [
    "Wiggum",
    "WiggumConfig",
    "RuleLoader",
    "load_rules_for_file",
    "get_review_prompt",
    "__version__",
]
