"""
Rule Loader - Loads compiled JSON rules for structured review enforcement.

Provides:
- Load rules by file type (*.cs, *.ts, etc.)
- Filter by severity (critical, major, minor, info)
- Generate structured review checklists
"""

import json
import fnmatch
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class Rule:
    """A single enforceable rule."""
    id: str
    title: str
    severity: str  # critical, major, minor, info
    check: str
    bad_example: Optional[str] = None
    good_example: Optional[str] = None
    rationale: Optional[str] = None
    auto_detectable: bool = True

    @property
    def is_blocking(self) -> bool:
        """Returns True if this rule blocks on failure."""
        return self.severity in ("critical", "major")


@dataclass
class RuleSet:
    """A collection of related rules."""
    id: str
    version: str
    domain: str
    applies_to: list[str]
    rules: list[Rule]

    def matches_file(self, filename: str) -> bool:
        """Check if this ruleset applies to the given file."""
        return any(fnmatch.fnmatch(filename, pattern) for pattern in self.applies_to)

    def get_blocking_rules(self) -> list[Rule]:
        """Get rules that block on failure (critical/major)."""
        return [r for r in self.rules if r.is_blocking]

    def get_warning_rules(self) -> list[Rule]:
        """Get rules that warn on failure (minor/info)."""
        return [r for r in self.rules if not r.is_blocking]


class RuleLoader:
    """Loads and manages compiled JSON rules."""

    def __init__(self, rules_dir: Optional[Path] = None):
        if rules_dir is None:
            # Default to .gemini/rules/compiled relative to this file
            self.rules_dir = Path(__file__).parent.parent / "rules" / "compiled"
        else:
            self.rules_dir = Path(rules_dir)

        self._cache: dict[str, RuleSet] = {}

    def load_all(self) -> list[RuleSet]:
        """Load all rule files from the compiled directory."""
        rulesets = []
        if not self.rules_dir.exists():
            return rulesets

        for rule_file in self.rules_dir.glob("*.rules.json"):
            ruleset = self._load_file(rule_file)
            if ruleset:
                rulesets.append(ruleset)
                self._cache[ruleset.id] = ruleset

        return rulesets

    def load_for_file(self, filename: str) -> list[RuleSet]:
        """Load all rulesets that apply to the given filename."""
        if not self._cache:
            self.load_all()

        return [rs for rs in self._cache.values() if rs.matches_file(filename)]

    def load_for_domain(self, domain: str) -> list[RuleSet]:
        """Load all rulesets for a specific domain (dotnet, typescript, general)."""
        if not self._cache:
            self.load_all()

        return [rs for rs in self._cache.values() if rs.domain == domain]

    def _load_file(self, path: Path) -> Optional[RuleSet]:
        """Load a single rule file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            rules = [
                Rule(
                    id=r["id"],
                    title=r["title"],
                    severity=r["severity"],
                    check=r["check"],
                    bad_example=r.get("bad_example"),
                    good_example=r.get("good_example"),
                    rationale=r.get("rationale"),
                    auto_detectable=r.get("auto_detectable", True)
                )
                for r in data.get("rules", [])
            ]

            return RuleSet(
                id=data["id"],
                version=data["version"],
                domain=data["domain"],
                applies_to=data.get("applies_to", []),
                rules=rules
            )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading {path}: {e}")
            return None

    def generate_checklist(self, filename: str) -> str:
        """Generate a structured checklist for reviewing a file."""
        rulesets = self.load_for_file(filename)
        if not rulesets:
            return f"No rules apply to {filename}"

        lines = [
            f"# Rule Checklist for {filename}",
            "",
            "## Instructions",
            "For EACH rule below, you MUST output a structured result:",
            "- PASS: Rule is satisfied",
            "- FAIL: Rule is violated (include specific line numbers and code)",
            "- N/A: Rule does not apply to this code",
            "",
            "## BLOCKING Rules (Critical/Major) - Must ALL pass",
            ""
        ]

        for rs in rulesets:
            blocking = rs.get_blocking_rules()
            if blocking:
                lines.append(f"### {rs.id} (v{rs.version})")
                for rule in blocking:
                    lines.append(f"- [ ] **{rule.id}**: {rule.title}")
                    lines.append(f"      Check: {rule.check}")
                    if rule.rationale:
                        lines.append(f"      Why: {rule.rationale}")
                lines.append("")

        lines.append("## Warning Rules (Minor/Info) - Should pass")
        lines.append("")

        for rs in rulesets:
            warnings = rs.get_warning_rules()
            if warnings:
                lines.append(f"### {rs.id}")
                for rule in warnings:
                    lines.append(f"- [ ] **{rule.id}**: {rule.title}")
                    lines.append(f"      Check: {rule.check}")
                lines.append("")

        return "\n".join(lines)

    def get_review_prompt(self, filename: str, code: str) -> str:
        """Generate a complete review prompt with rules and code."""
        rulesets = self.load_for_file(filename)
        if not rulesets:
            return f"No rules apply to {filename}. Review for general quality."

        # Collect all rules
        blocking_rules = []
        warning_rules = []

        for rs in rulesets:
            blocking_rules.extend(rs.get_blocking_rules())
            warning_rules.extend(rs.get_warning_rules())

        prompt = f"""# Structured Code Review

## File: {filename}

## Code to Review:
```
{code}
```

## MANDATORY REVIEW PROTOCOL

You MUST check EVERY rule below and output a structured result for EACH.
Use this EXACT format for each rule:

```
RULE: <rule-id>
STATUS: PASS | FAIL | N/A
EVIDENCE: <specific code or "Rule satisfied" or "Does not apply">
```

### BLOCKING RULES (Critical/Major)
If ANY blocking rule fails, the review result is BLOCKED.

"""
        for rule in blocking_rules:
            prompt += f"""
#### {rule.id}: {rule.title}
- Severity: {rule.severity.upper()}
- Check: {rule.check}
"""
            if rule.bad_example:
                prompt += f"- Bad: `{rule.bad_example}`\n"
            if rule.good_example:
                prompt += f"- Good: `{rule.good_example}`\n"

        prompt += """

### WARNING RULES (Minor/Info)
These should pass but don't block.

"""
        for rule in warning_rules:
            prompt += f"""
#### {rule.id}: {rule.title}
- Severity: {rule.severity}
- Check: {rule.check}
"""

        prompt += """

## OUTPUT FORMAT

After checking all rules, output a summary:

```
REVIEW RESULT: PASS | BLOCKED | WARNINGS

BLOCKING FAILURES:
- <rule-id>: <issue>

WARNINGS:
- <rule-id>: <issue>

SUMMARY:
<brief overall assessment>
```

If REVIEW RESULT is BLOCKED, the code MUST be fixed before proceeding.
"""

        return prompt


# Convenience function for quick loading
def load_rules_for_file(filename: str) -> list[RuleSet]:
    """Quick helper to load rules for a file."""
    return RuleLoader().load_for_file(filename)


def get_review_prompt(filename: str, code: str) -> str:
    """Quick helper to generate a review prompt."""
    return RuleLoader().get_review_prompt(filename, code)


if __name__ == "__main__":
    # Test the loader
    loader = RuleLoader()
    rulesets = loader.load_all()

    print(f"Loaded {len(rulesets)} rulesets:")
    for rs in rulesets:
        print(f"  - {rs.id}: {len(rs.rules)} rules ({rs.domain})")
        blocking = len(rs.get_blocking_rules())
        print(f"    Blocking: {blocking}, Warnings: {len(rs.rules) - blocking}")

    print("\nChecklist for GreetingService.cs:")
    print(loader.generate_checklist("GreetingService.cs"))
