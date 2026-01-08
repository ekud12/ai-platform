#!/usr/bin/env python3
"""
CLI entry point for Wiggum.

Usage:
    python -m wiggum --spec path/to/spec.md
    python -m wiggum --spec path/to/spec.md --plan-only
    python -m wiggum --spec path/to/spec.md --dry-run --verbose
"""

import sys
import argparse
import json
from pathlib import Path


def setup_path():
    """Add parent directories to path for imports."""
    # When run as: python -m .gemini.wiggum
    # We need to ensure .gemini/tools is in path for loader.py
    script_dir = Path(__file__).parent
    gemini_root = script_dir.parent
    tools_dir = gemini_root / "tools"

    for path in [str(gemini_root), str(tools_dir)]:
        if path not in sys.path:
            sys.path.insert(0, path)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="wiggum",
        description="Wiggum - Autonomous Agent Loop for Gemini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run full autonomous loop
    python -m wiggum --spec specs/new-feature.md

    # Plan only (no execution)
    python -m wiggum --spec specs/new-feature.md --plan-only

    # Dry run (no file writes)
    python -m wiggum --spec specs/new-feature.md --dry-run

    # Verbose output
    python -m wiggum --spec specs/new-feature.md --verbose

Environment Variables:
    GEMINI_API_KEY      Required. Your Gemini API key.
    WIGGUM_MODEL        Model to use (default: gemini-2.0-flash)
    WIGGUM_RATE_LIMIT   Max API calls per hour (default: 100)
    WIGGUM_MAX_STEPS    Max steps per run (default: 50)
    WIGGUM_DRY_RUN      Set to 'true' for dry run mode
    WIGGUM_VERBOSE      Set to 'true' for verbose output
        """
    )

    parser.add_argument(
        "--spec", "-s",
        required=True,
        help="Path to the feature specification markdown file"
    )

    parser.add_argument(
        "--plan-only", "-p",
        action="store_true",
        help="Only generate plan, don't execute"
    )

    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Don't actually write files"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--no-review",
        action="store_true",
        help="Skip review phase"
    )

    parser.add_argument(
        "--no-meta",
        action="store_true",
        help="Skip meta check phase"
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=50,
        help="Maximum steps to execute (default: 50)"
    )

    parser.add_argument(
        "--max-time",
        type=int,
        default=3600,
        help="Maximum runtime in seconds (default: 3600)"
    )

    parser.add_argument(
        "--output", "-o",
        help="Output file for results (JSON)"
    )

    args = parser.parse_args()

    # Setup paths
    setup_path()

    # Import after path setup
    try:
        from .config import WiggumConfig
        from .core import Wiggum
    except ImportError:
        # Handle direct execution
        from config import WiggumConfig
        from core import Wiggum

    # Create configuration
    try:
        config = WiggumConfig(
            dry_run=args.dry_run,
            verbose=args.verbose,
            enable_review=not args.no_review,
            enable_meta_check=not args.no_meta,
            max_steps=args.max_steps,
            max_runtime_seconds=args.max_time,
        )
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Make sure GEMINI_API_KEY environment variable is set.")
        sys.exit(1)

    # Create Wiggum instance
    wiggum = Wiggum(config)

    # Progress callback
    def on_progress(progress: dict):
        if args.verbose:
            pct = progress.get("progress_percent", 0)
            steps = progress.get("steps_completed", 0)
            print(f"   Progress: {pct}% ({steps} steps)")

    # Run
    print()
    print("=" * 60)
    print("  WIGGUM - Autonomous Agent Loop")
    print("=" * 60)
    print()

    if args.plan_only:
        plan = wiggum.run_plan_only(args.spec)

        if plan:
            print("\nGenerated Plan:")
            print("-" * 40)
            for step in plan.get("plan", []):
                print(f"  {step.get('step', '?')}. [{step.get('role', '?')}] {step.get('instruction', '?')}")
            print()

            if args.output:
                with open(args.output, "w") as f:
                    json.dump(plan, f, indent=2)
                print(f"Plan saved to: {args.output}")

            sys.exit(0)
        else:
            print("Failed to generate plan.")
            sys.exit(1)

    else:
        result = wiggum.run(args.spec, on_progress=on_progress)

        print()
        print("=" * 60)
        print("  RESULTS")
        print("=" * 60)
        print()
        print(f"  Status:     {'SUCCESS' if result.success else 'FAILED'}")
        print(f"  Reason:     {result.exit_reason.value}")
        print(f"  Message:    {result.message}")
        print(f"  Steps:      {result.steps_completed}")
        print(f"  Time:       {result.elapsed_seconds:.1f}s")
        print(f"  Files:      {len(result.files_changed)}")

        if result.files_changed:
            print()
            print("  Files Changed:")
            for f in result.files_changed[:10]:
                print(f"    - {f}")
            if len(result.files_changed) > 10:
                print(f"    ... and {len(result.files_changed) - 10} more")

        if result.errors:
            print()
            print("  Errors:")
            for e in result.errors[:5]:
                print(f"    - {e}")

        print()

        # Save results
        if args.output:
            output_data = {
                "success": result.success,
                "exit_reason": result.exit_reason.value,
                "message": result.message,
                "steps_completed": result.steps_completed,
                "elapsed_seconds": result.elapsed_seconds,
                "files_changed": result.files_changed,
                "errors": result.errors,
            }

            if result.plan:
                output_data["plan"] = result.plan

            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=2)

            print(f"Results saved to: {args.output}")

        sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
