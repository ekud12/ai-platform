#!/usr/bin/env python3
"""
Core orchestration loop for Wiggum.

This is the main brain of the autonomous agent system.
"""

import json
import time
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

from .config import WiggumConfig
from .tools import WiggumTools
from .agents import AgentInvoker, AgentResponse
from .rate_limiter import AdaptiveRateLimiter
from .circuit_breaker import CircuitBreaker, RetryWithCircuitBreaker, CircuitBreakerError
from .exit_detector import ExitDetector, ExitReason, MetaVerdictChecker


@dataclass
class WiggumResult:
    """Result of a Wiggum run."""
    success: bool
    exit_reason: ExitReason
    message: str
    steps_completed: int
    files_changed: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    plan: Optional[dict] = None
    reviews: list[dict] = field(default_factory=list)
    meta_verdict: Optional[dict] = None
    errors: list[str] = field(default_factory=list)


class Wiggum:
    """
    The Autonomous Agent Loop.

    Orchestrates:
    1. Planning - Break spec into tasks
    2. Execution - Run coders on each task
    3. Review - Validate code against rules
    4. Meta - Final compliance check
    5. Memory - Update lessons learned
    """

    def __init__(self, config: Optional[WiggumConfig] = None):
        self.config = config or WiggumConfig.from_env()

        # Initialize components
        self.tools = WiggumTools(
            workspace_root=self.config.workspace_root,
            dry_run=self.config.dry_run,
            verbose=self.config.verbose
        )

        self.agents = AgentInvoker(self.config, self.tools)

        self.rate_limiter = AdaptiveRateLimiter(
            max_per_hour=self.config.max_calls_per_hour,
            max_per_minute=self.config.max_calls_per_minute,
        )

        self.circuit_breaker = CircuitBreaker(
            max_failures=self.config.max_consecutive_failures,
            reset_timeout=self.config.failure_reset_seconds,
        )

        self.retry_executor = RetryWithCircuitBreaker(
            max_retries=self.config.max_retries,
            base_delay=self.config.retry_delay_seconds,
            circuit_breaker=self.circuit_breaker,
        )

        self.exit_detector = ExitDetector(
            workspace_root=self.config.workspace_root,
            max_steps=self.config.max_steps,
            max_runtime_seconds=self.config.max_runtime_seconds,
            max_consecutive_failures=self.config.max_consecutive_failures,
        )

        self.meta_checker = MetaVerdictChecker()

        # Run state
        self._all_files_changed: list[str] = []
        self._all_reviews: list[dict] = []
        self._errors: list[str] = []

    def _log(self, message: str, level: str = "INFO"):
        """Log a message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "   ",
            "STEP": "=>",
            "OK": " ✓",
            "WARN": " ⚠",
            "ERROR": " ✗",
            "PHASE": "\n##",
        }.get(level, "   ")

        print(f"[{timestamp}] {prefix} {message}")

        # Also log to file
        if self.config.logs_dir.exists():
            log_file = self.config.logs_dir / "wiggum.log"
            with open(log_file, "a") as f:
                f.write(f"[{timestamp}] [{level}] {message}\n")

    def _get_domain_agent(self, task: str) -> tuple[str, str]:
        """
        Determine which coder and reviewer to use based on task.

        Returns:
            Tuple of (coder_agent_name, reviewer_agent_name)
        """
        task_lower = task.lower()

        # Check for TypeScript/JavaScript indicators
        ts_indicators = [".ts", ".tsx", ".js", ".jsx", "typescript", "javascript",
                         "react", "node", "npm", "frontend", "component"]
        for indicator in ts_indicators:
            if indicator in task_lower:
                return "coder-typescript", "reviewer-typescript"

        # Check for .NET indicators
        dotnet_indicators = [".cs", "c#", "csharp", ".net", "dotnet", "asp.net",
                            "entity", "backend", "api", "controller", "service"]
        for indicator in dotnet_indicators:
            if indicator in task_lower:
                return "coder-dotnet", "reviewer-dotnet"

        # Default to .NET (based on project type)
        return "coder-dotnet", "reviewer-dotnet"

    def run(self, spec_path: str, on_progress: Optional[Callable[[dict], None]] = None) -> WiggumResult:
        """
        Run the Wiggum autonomous loop.

        Args:
            spec_path: Path to the feature specification markdown
            on_progress: Optional callback for progress updates

        Returns:
            WiggumResult with outcome
        """
        start_time = time.time()
        self.exit_detector.reset()
        self._all_files_changed = []
        self._all_reviews = []
        self._errors = []

        spec_file = Path(spec_path)
        if not spec_file.exists():
            return WiggumResult(
                success=False,
                exit_reason=ExitReason.UNRECOVERABLE_ERROR,
                message=f"Spec file not found: {spec_path}",
                steps_completed=0,
                errors=[f"File not found: {spec_path}"]
            )

        spec_content = spec_file.read_text()
        self._log(f"Starting Wiggum on '{spec_file.name}'", "PHASE")

        # ============================================
        # PHASE 1: PLANNING
        # ============================================
        self._log("PHASE 1: Planning", "PHASE")

        try:
            self.rate_limiter.acquire()
            plan = self.retry_executor.execute(
                lambda: self.agents.invoke_planner(spec_content)
            )
        except CircuitBreakerError as e:
            return WiggumResult(
                success=False,
                exit_reason=ExitReason.CIRCUIT_BREAKER_OPEN,
                message=str(e),
                steps_completed=0,
                elapsed_seconds=time.time() - start_time,
                errors=[str(e)]
            )
        except Exception as e:
            self._errors.append(f"Planning failed: {str(e)}")
            return WiggumResult(
                success=False,
                exit_reason=ExitReason.UNRECOVERABLE_ERROR,
                message=f"Planning failed: {str(e)}",
                steps_completed=0,
                elapsed_seconds=time.time() - start_time,
                errors=self._errors
            )

        if not plan or not plan.get("plan"):
            return WiggumResult(
                success=False,
                exit_reason=ExitReason.UNRECOVERABLE_ERROR,
                message="Planner failed to generate a valid plan",
                steps_completed=0,
                elapsed_seconds=time.time() - start_time,
                errors=["Invalid plan structure"]
            )

        steps = plan["plan"]
        self._log(f"Plan generated with {len(steps)} steps", "OK")

        # ============================================
        # PHASE 2 & 3: EXECUTION + REVIEW LOOP
        # ============================================
        self._log("PHASE 2-3: Execution & Review", "PHASE")

        for i, step in enumerate(steps):
            step_id = step.get("step", i + 1)
            instruction = step.get("instruction", "")
            role = step.get("role", "")

            self._log(f"Step {step_id}: {instruction[:60]}...", "STEP")

            # Check exit conditions
            exit_status = self.exit_detector.check(
                plan_remaining=len(steps) - i - 1,
                rate_limit_remaining=self.rate_limiter.get_remaining(),
                circuit_state=self.circuit_breaker.state.value
            )

            if exit_status.should_exit:
                return WiggumResult(
                    success=exit_status.reason in [ExitReason.ALL_STEPS_DONE, ExitReason.TASK_COMPLETE],
                    exit_reason=exit_status.reason,
                    message=exit_status.message,
                    steps_completed=i,
                    files_changed=self._all_files_changed,
                    elapsed_seconds=time.time() - start_time,
                    plan=plan,
                    reviews=self._all_reviews,
                    errors=self._errors
                )

            # Determine agents
            coder_agent, reviewer_agent = self._get_domain_agent(instruction)

            # Execute coder
            try:
                self.rate_limiter.acquire()
                coder_response = self.retry_executor.execute(
                    lambda: self.agents.invoke_agent(
                        coder_agent,
                        task=instruction,
                        context=spec_content
                    )
                )

                if coder_response.success:
                    self._log(f"Coder completed: {coder_response.content[:60]}...", "OK")
                    self._all_files_changed.extend(coder_response.files_changed)
                    self.rate_limiter.record_success()
                    self.exit_detector.record_step(success=True, task_id=f"step-{step_id}")
                else:
                    self._log(f"Coder failed: {coder_response.error}", "ERROR")
                    self._errors.append(f"Step {step_id}: {coder_response.error}")
                    self.rate_limiter.record_failure()
                    self.exit_detector.record_step(success=False)
                    continue

            except CircuitBreakerError as e:
                return WiggumResult(
                    success=False,
                    exit_reason=ExitReason.CIRCUIT_BREAKER_OPEN,
                    message=str(e),
                    steps_completed=i,
                    files_changed=self._all_files_changed,
                    elapsed_seconds=time.time() - start_time,
                    plan=plan,
                    reviews=self._all_reviews,
                    errors=self._errors + [str(e)]
                )
            except Exception as e:
                self._log(f"Coder error: {str(e)}", "ERROR")
                self._errors.append(f"Step {step_id}: {str(e)}")
                self.exit_detector.record_step(success=False)
                continue

            # Execute reviewer (if enabled)
            if self.config.enable_review and coder_response.files_changed:
                self._log(f"Reviewing with {reviewer_agent}...", "INFO")

                try:
                    self.rate_limiter.acquire()

                    # Build code changes summary
                    changes_summary = "\n".join([
                        f"File: {f}" for f in coder_response.files_changed
                    ])
                    changes_summary += f"\n\nAgent output:\n{coder_response.content}"

                    review_result = self.agents.invoke_reviewer(
                        reviewer_agent,
                        code_changes=changes_summary,
                        task=instruction
                    )

                    self._all_reviews.append({
                        "step": step_id,
                        "reviewer": reviewer_agent,
                        "result": review_result
                    })

                    status = review_result.get("status", "UNKNOWN").upper()
                    if status in ["PASS", "APPROVED", "OK"]:
                        self._log(f"Review passed", "OK")
                    elif status in ["BLOCK", "REJECTED", "FAIL"]:
                        self._log(f"Review blocked: {review_result.get('issues', [])}", "WARN")
                        # Could implement retry with feedback here
                    else:
                        self._log(f"Review result: {status}", "INFO")

                except Exception as e:
                    self._log(f"Review error: {str(e)}", "WARN")
                    # Don't fail the whole run for review errors

            # Progress callback
            if on_progress:
                on_progress(self.exit_detector.get_progress())

        # ============================================
        # PHASE 4: META CHECK
        # ============================================
        if self.config.enable_meta_check and self._all_files_changed:
            self._log("PHASE 4: Meta Check", "PHASE")

            try:
                self.rate_limiter.acquire()

                changes_summary = f"Files changed: {', '.join(self._all_files_changed)}"
                meta_verdict = self.agents.invoke_meta(changes_summary, self._all_reviews)

                verdict_status = self.meta_checker.check_verdict(meta_verdict)

                if verdict_status.reason == ExitReason.META_REJECTED:
                    self._log(f"Meta rejected: {meta_verdict.get('reason', 'Unknown')}", "ERROR")
                    return WiggumResult(
                        success=False,
                        exit_reason=ExitReason.META_REJECTED,
                        message=verdict_status.message,
                        steps_completed=len(steps),
                        files_changed=self._all_files_changed,
                        elapsed_seconds=time.time() - start_time,
                        plan=plan,
                        reviews=self._all_reviews,
                        meta_verdict=meta_verdict,
                        errors=self._errors
                    )
                else:
                    self._log("Meta approved", "OK")

            except Exception as e:
                self._log(f"Meta check error: {str(e)}", "WARN")
                # Don't fail for meta errors

        # ============================================
        # PHASE 5: MEMORY COMMIT
        # ============================================
        self._log("PHASE 5: Memory Commit", "PHASE")

        # Update lessons learned
        if self._all_files_changed:
            lessons_file = self.config.workspace_root / "docs" / "LESSONS.md"
            if lessons_file.exists():
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                lesson_entry = f"\n## Wiggum Run - {timestamp}\n"
                lesson_entry += f"- Spec: {spec_file.name}\n"
                lesson_entry += f"- Steps: {len(steps)}\n"
                lesson_entry += f"- Files: {', '.join(self._all_files_changed[:5])}\n"

                if not self.config.dry_run:
                    with open(lessons_file, "a") as f:
                        f.write(lesson_entry)
                    self._log("Updated LESSONS.md", "OK")

        # Regenerate architecture map
        map_script = self.config.gemini_root / "tools" / "generate-map.js"
        if map_script.exists() and not self.config.dry_run:
            import subprocess
            try:
                subprocess.run(
                    ["node", str(map_script)],
                    cwd=str(self.config.workspace_root),
                    capture_output=True,
                    timeout=30
                )
                self._log("Updated ARCHITECTURE.md", "OK")
            except:
                pass  # Non-critical

        # ============================================
        # DONE
        # ============================================
        elapsed = time.time() - start_time
        self._log(f"Completed in {elapsed:.1f}s", "PHASE")

        return WiggumResult(
            success=True,
            exit_reason=ExitReason.ALL_STEPS_DONE,
            message=f"Successfully completed {len(steps)} steps",
            steps_completed=len(steps),
            files_changed=self._all_files_changed,
            elapsed_seconds=elapsed,
            plan=plan,
            reviews=self._all_reviews,
            errors=self._errors
        )

    def run_plan_only(self, spec_path: str) -> Optional[dict]:
        """
        Run only the planning phase.

        Args:
            spec_path: Path to the feature specification

        Returns:
            Plan dictionary or None
        """
        spec_file = Path(spec_path)
        if not spec_file.exists():
            self._log(f"Spec file not found: {spec_path}", "ERROR")
            return None

        spec_content = spec_file.read_text()
        self._log(f"Planning for '{spec_file.name}'", "PHASE")

        try:
            self.rate_limiter.acquire()
            plan = self.agents.invoke_planner(spec_content)

            if plan and plan.get("plan"):
                self._log(f"Generated plan with {len(plan['plan'])} steps", "OK")
                return plan
            else:
                self._log("Failed to generate plan", "ERROR")
                return None

        except Exception as e:
            self._log(f"Planning failed: {str(e)}", "ERROR")
            return None
