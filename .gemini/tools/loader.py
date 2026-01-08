#!/usr/bin/env python3
"""
Loader for ADK integration. Not used by Gemini CLI directly.
Usage: from loader import load_agent

Requires: Python 3.8+, PyYAML
"""
import yaml
from pathlib import Path
from typing import Optional

MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"

def load_manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text())

def load_agent(name: str, include_constitution: bool = True) -> str:
    """Load an agent's complete system prompt."""
    manifest = load_manifest()
    base = Path(__file__).parent.parent

    if name not in manifest["agents"]:
        raise ValueError(f"Unknown agent: {name}")

    agent_config = manifest["agents"][name]

    # Load agent definition
    definition = (base / agent_config["definition"]).read_text()

    # Load rules
    rules_content = []
    for rule_pattern in agent_config.get("rules", []):
        if "*" in rule_pattern:
            for rule_file in base.glob(rule_pattern):
                rules_content.append(rule_file.read_text())
        else:
            rules_content.append((base / rule_pattern).read_text())

    # Load constitution if requested
    constitution = ""
    if include_constitution:
        for const_path in manifest.get("constitution", []):
            constitution += (base / const_path).read_text() + "\n"

    return f"{constitution}\n{definition}\n\n# Rules\n\n" + "\n\n".join(rules_content)
