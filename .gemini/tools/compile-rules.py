#!/usr/bin/env python3
"""
Rule Compiler - Converts markdown rules to compiled JSON format.

This script mirrors the rules/ folder structure into rules/compiled/
For each *.rules.md file, it generates a corresponding *.rules.json file.

Usage:
    python compile-rules.py              # Compile changed rules only (incremental)
    python compile-rules.py --force      # Recompile all rules
    python compile-rules.py --check      # Check if recompilation needed (exit 1 if stale)
    python compile-rules.py --watch      # Watch for changes and recompile
    python compile-rules.py --validate   # Validate existing JSON against schema

Performance:
    - Incremental by default: only recompiles if source is newer than target
    - Typical run: <100ms for unchanged files, ~500ms for full recompile
"""

import re
import json
import argparse
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Rule:
    id: str
    title: str
    severity: str
    check: str
    bad_example: Optional[str] = None
    good_example: Optional[str] = None
    rationale: Optional[str] = None


@dataclass
class RuleSet:
    id: str
    version: str
    domain: str
    applies_to: list[str]
    rules: list[dict]


# Domain to file extensions mapping
DOMAIN_EXTENSIONS = {
    "dotnet": ["*.cs", "*.csx"],
    "typescript": ["*.ts", "*.tsx"],
    "javascript": ["*.js", "*.jsx", "*.mjs"],
    "constitution": ["*"],
}

# Severity normalization
SEVERITY_MAP = {
    "critical": "critical",
    "major": "major",
    "minor": "minor",
    "info": "info",
    "warning": "minor",
}


def extract_code_block(text: str) -> Optional[str]:
    """Extract code from a markdown code block."""
    match = re.search(r'```\w*\n(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def parse_rule_section(section: str) -> Optional[Rule]:
    """Parse a single rule section from markdown."""
    header_match = re.match(r'^##\s+([A-Z]{2,4}-[A-Z]{2,6}-\d{3})\s*[—-]\s*(.+)$', section.strip(), re.MULTILINE)
    if not header_match:
        return None

    rule_id = header_match.group(1)
    title = header_match.group(2).strip()

    severity_match = re.search(r'\*\*Severity:\s*(\w+)\*\*', section, re.IGNORECASE)
    severity = "info"
    if severity_match:
        raw_severity = severity_match.group(1).lower()
        severity = SEVERITY_MAP.get(raw_severity, "info")

    rule_match = re.search(r'\*\*Rule\*\*\s*\n(.+?)(?=\*\*(?:Bad|Good|Scope|Related|Rationale)|---|\Z)', section, re.DOTALL)
    check = ""
    if rule_match:
        check = rule_match.group(1).strip()
        check = re.sub(r'`([^`]+)`', r'\1', check)
        check = check.replace('\n', ' ').strip()

    bad_match = re.search(r'\*\*Bad Pattern\*\*\s*\n(```.*?```)', section, re.DOTALL)
    bad_example = None
    if bad_match:
        bad_example = extract_code_block(bad_match.group(1))

    good_match = re.search(r'\*\*(?:Good|Recommended) Pattern\*\*\s*\n(```.*?```)', section, re.DOTALL)
    good_example = None
    if good_match:
        good_example = extract_code_block(good_match.group(1))

    rationale_match = re.search(r'\*\*Rationale\*\*\s*\n(.+?)(?=\*\*|---|\Z)', section, re.DOTALL)
    rationale = None
    if rationale_match:
        rationale = rationale_match.group(1).strip()

    return Rule(
        id=rule_id,
        title=title,
        severity=severity,
        check=check,
        bad_example=bad_example,
        good_example=good_example,
        rationale=rationale
    )


def parse_rules_file(filepath: Path) -> list[Rule]:
    """Parse all rules from a markdown file."""
    content = filepath.read_text(encoding='utf-8')
    sections = re.split(r'(?=^## [A-Z]{2,4}-[A-Z]{2,6}-\d{3})', content, flags=re.MULTILINE)

    rules = []
    for section in sections:
        if section.strip():
            rule = parse_rule_section(section)
            if rule:
                rules.append(rule)

    return rules


def determine_domain(filepath: Path) -> str:
    """Determine domain from file path."""
    parts = filepath.parts
    for part in parts:
        if part in DOMAIN_EXTENSIONS:
            return part
    return "general"


def get_output_path(source: Path, output_dir: Path) -> Path:
    """Get the output path for a source file."""
    domain = determine_domain(source)
    name = source.stem.replace('.rules', '')
    ruleset_id = f"{domain}-{name}"
    return output_dir / f"{ruleset_id}.rules.json"


def needs_recompile(source: Path, target: Path) -> bool:
    """Check if source is newer than target."""
    if not target.exists():
        return True
    return source.stat().st_mtime > target.stat().st_mtime


def compile_rules_file(source: Path, output_dir: Path) -> Optional[Path]:
    """Compile a single markdown rules file to JSON."""
    rules = parse_rules_file(source)

    # Even if no rules, create empty ruleset to mark as processed
    # This prevents "stale" detection on files with different formats

    domain = determine_domain(source)
    name = source.stem.replace('.rules', '')
    ruleset_id = f"{domain}-{name}"

    ruleset = RuleSet(
        id=ruleset_id,
        version="1.0.0",
        domain=domain,
        applies_to=DOMAIN_EXTENSIONS.get(domain, ["*"]),
        rules=[asdict(r) for r in rules]
    )

    for rule in ruleset.rules:
        keys_to_remove = [k for k, v in rule.items() if v is None]
        for k in keys_to_remove:
            del rule[k]

    output_file = output_dir / f"{ruleset_id}.rules.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(ruleset), f, indent=2, ensure_ascii=False)

    return output_file


def compile_all_rules(rules_dir: Path, output_dir: Path, force: bool = False, verbose: bool = True) -> dict:
    """Compile all markdown rules to JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)

    stats = {
        "files_processed": 0,
        "files_skipped": 0,
        "rules_compiled": 0,
        "errors": [],
        "outputs": []
    }

    for md_file in rules_dir.rglob("*.rules.md"):
        if "compiled" in md_file.parts:
            continue

        output_file = get_output_path(md_file, output_dir)

        # Incremental: skip if not changed
        if not force and not needs_recompile(md_file, output_file):
            stats["files_skipped"] += 1
            continue

        if verbose:
            print(f"Compiling: {md_file.relative_to(rules_dir)}")

        try:
            result = compile_rules_file(md_file, output_dir)
            if result:
                with open(result) as f:
                    data = json.load(f)
                    rule_count = len(data.get("rules", []))

                stats["files_processed"] += 1
                stats["rules_compiled"] += rule_count
                stats["outputs"].append(str(result.name))

                if verbose:
                    print(f"  -> {result.name} ({rule_count} rules)")
            else:
                if verbose:
                    print(f"  (no rules found)")

        except Exception as e:
            stats["errors"].append(f"{md_file.name}: {str(e)}")
            if verbose:
                print(f"  ERROR: {e}")

    return stats


def check_stale(rules_dir: Path, output_dir: Path) -> list[Path]:
    """Check which files need recompilation."""
    stale = []
    for md_file in rules_dir.rglob("*.rules.md"):
        if "compiled" in md_file.parts:
            continue
        output_file = get_output_path(md_file, output_dir)
        if needs_recompile(md_file, output_file):
            stale.append(md_file)
    return stale


def validate_compiled_rules(compiled_dir: Path, schema_path: Path) -> dict:
    """Validate compiled JSON files against schema."""
    try:
        import jsonschema
    except ImportError:
        return {"error": "jsonschema package not installed. Run: pip install jsonschema"}

    with open(schema_path) as f:
        schema = json.load(f)

    results = {"valid": [], "invalid": []}

    for json_file in compiled_dir.glob("*.rules.json"):
        with open(json_file) as f:
            data = json.load(f)

        try:
            jsonschema.validate(data, schema)
            results["valid"].append(json_file.name)
        except jsonschema.ValidationError as e:
            results["invalid"].append({
                "file": json_file.name,
                "error": str(e.message)
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="Compile markdown rules to JSON")
    parser.add_argument("--force", action="store_true", help="Force recompile all (ignore timestamps)")
    parser.add_argument("--check", action="store_true", help="Check if recompilation needed (exit 1 if stale)")
    parser.add_argument("--watch", action="store_true", help="Watch for changes")
    parser.add_argument("--validate", action="store_true", help="Validate compiled JSON")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    rules_dir = script_dir.parent / "rules"
    compiled_dir = rules_dir / "compiled"
    schema_path = rules_dir / "rule.schema.json"

    # Check mode: just report if stale, exit 1 if recompilation needed
    if args.check:
        stale = check_stale(rules_dir, compiled_dir)
        if stale:
            print(f"Stale rules detected ({len(stale)} files need recompilation):")
            for f in stale[:5]:  # Show first 5
                print(f"  - {f.relative_to(rules_dir)}")
            if len(stale) > 5:
                print(f"  ... and {len(stale) - 5} more")
            return 1
        else:
            if not args.quiet:
                print("All compiled rules are up to date.")
            return 0

    if args.validate:
        if not schema_path.exists():
            print(f"Schema not found: {schema_path}")
            return 1

        print("Validating compiled rules...")
        results = validate_compiled_rules(compiled_dir, schema_path)

        print(f"\nValid: {len(results.get('valid', []))}")
        for f in results.get("valid", []):
            print(f"  + {f}")

        if results.get("invalid"):
            print(f"\nInvalid: {len(results['invalid'])}")
            for item in results["invalid"]:
                print(f"  - {item['file']}: {item['error']}")
            return 1

        return 0

    if args.watch:
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class RulesHandler(FileSystemEventHandler):
                def on_modified(self, event):
                    if event.src_path.endswith('.rules.md'):
                        print(f"\nChange detected: {event.src_path}")
                        compile_all_rules(rules_dir, compiled_dir, force=False, verbose=not args.quiet)

            observer = Observer()
            observer.schedule(RulesHandler(), str(rules_dir), recursive=True)
            observer.start()

            print(f"Watching {rules_dir} for changes... (Ctrl+C to stop)")
            import time
            while True:
                time.sleep(1)

        except ImportError:
            print("watchdog package not installed. Run: pip install watchdog")
            return 1
        except KeyboardInterrupt:
            observer.stop()
            observer.join()
            return 0

    # Default: incremental compile
    if not args.quiet:
        print(f"Compiling rules from: {rules_dir}")
        print(f"Output directory: {compiled_dir}")
        if not args.force:
            print("(incremental mode - use --force to recompile all)")
        print()

    stats = compile_all_rules(rules_dir, compiled_dir, force=args.force, verbose=not args.quiet)

    if not args.quiet:
        print()
        print("=" * 50)
        print(f"Files compiled: {stats['files_processed']}")
        print(f"Files skipped:  {stats['files_skipped']} (unchanged)")
        print(f"Rules total:    {stats['rules_compiled']}")

        if stats["errors"]:
            print(f"Errors: {len(stats['errors'])}")
            for err in stats["errors"]:
                print(f"  - {err}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
