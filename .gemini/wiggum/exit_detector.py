#!/usr/bin/env python3
"""
Exit detection for Wiggum.

Determines when the autonomous loop should stop based on:
- Completion signals from agents
- Error conditions
- Resource limits
- Time limits
"""

import re
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


class ExitReason(Enum):
    """Reasons for exiting the loop."""
    NOT_EXITED = "not_exited"
    TASK_COMPLETE = "task_complete"
    ALL_STEPS_DONE = "all_steps_done"
    MAX_STEPS_REACHED = "max_steps_reached"
    MAX_TIME_REACHED = "max_time_reached"
    MAX_FAILURES_REACHED = "max_failures_reached"
    RATE_LIMIT_EXHAUSTED = "rate_limit_exhausted"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    USER_ABORT = "user_abort"
    PANIC_FILE_DETECTED = "panic_file_detected"
    META_REJECTED = "meta_rejected"
    UNRECOVERABLE_ERROR = "unrecoverable_error"


@dataclass
class ExitStatus:
    """Status of exit detection."""
    should_exit: bool
    reason: ExitReason
    message: str
    details: dict = field(default_factory=dict)


class ExitDetector:
    """
    Detects when the Wiggum loop should exit.

    Monitors multiple signals to determine completion or failure.
    """

    def __init__(
        self,
        workspace_root: Path,
        max_steps: int = 50,
        max_runtime_seconds: int = 3600,
        max_consecutive_failures: int = 5
    ):
        self.workspace_root = workspace_root
        self.max_steps = max_steps
        self.max_runtime_seconds = max_runtime_seconds
        self.max_consecutive_failures = max_consecutive_failures

        self._start_time = time.time()
        self._step_count = 0
        self._consecutive_failures = 0
        self._completed_tasks: list[str] = []
        self._user_aborted = False

        # Completion signal patterns
        self._completion_patterns = [
            r"task.{0,5}complete",
            r"all.{0,5}done",
            r"successfully.{0,10}completed",
            r"implementation.{0,5}complete",
            r"finished.{0,10}all",
            r"no.{0,5}more.{0,5}tasks",
        ]

    def reset(self):
        """Reset detector state for a new run."""
        self._start_time = time.time()
        self._step_count = 0
        self._consecutive_failures = 0
        self._completed_tasks = []
        self._user_aborted = False

    def record_step(self, success: bool = True, task_id: Optional[str] = None):
        """Record completion of a step."""
        self._step_count += 1

        if success:
            self._consecutive_failures = 0
            if task_id:
                self._completed_tasks.append(task_id)
        else:
            self._consecutive_failures += 1

    def signal_abort(self):
        """Signal user abort."""
        self._user_aborted = True

    def _check_panic_file(self) -> bool:
        """Check if .panic file exists."""
        panic_file = self.workspace_root / ".panic"
        return panic_file.exists()

    def _check_completion_signals(self, text: str) -> bool:
        """Check if text contains completion signals."""
        text_lower = text.lower()
        for pattern in self._completion_patterns:
            if re.search(pattern, text_lower):
                return True
        return False

    def check(
        self,
        plan_remaining: int = 0,
        agent_response: str = "",
        rate_limit_remaining: Optional[tuple[int, int]] = None,
        circuit_state: Optional[str] = None
    ) -> ExitStatus:
        """
        Check if loop should exit.

        Args:
            plan_remaining: Number of steps remaining in plan
            agent_response: Latest agent response text
            rate_limit_remaining: (hourly, minutely) remaining calls
            circuit_state: Current circuit breaker state

        Returns:
            ExitStatus indicating if and why to exit
        """
        # Check panic file first (highest priority)
        if self._check_panic_file():
            return ExitStatus(
                should_exit=True,
                reason=ExitReason.PANIC_FILE_DETECTED,
                message="Panic file detected - emergency stop"
            )

        # Check user abort
        if self._user_aborted:
            return ExitStatus(
                should_exit=True,
                reason=ExitReason.USER_ABORT,
                message="User requested abort"
            )

        # Check circuit breaker
        if circuit_state == "open":
            return ExitStatus(
                should_exit=True,
                reason=ExitReason.CIRCUIT_BREAKER_OPEN,
                message="Circuit breaker is open - too many failures"
            )

        # Check consecutive failures
        if self._consecutive_failures >= self.max_consecutive_failures:
            return ExitStatus(
                should_exit=True,
                reason=ExitReason.MAX_FAILURES_REACHED,
                message=f"Reached {self.max_consecutive_failures} consecutive failures"
            )

        # Check step limit
        if self._step_count >= self.max_steps:
            return ExitStatus(
                should_exit=True,
                reason=ExitReason.MAX_STEPS_REACHED,
                message=f"Reached maximum steps ({self.max_steps})",
                details={"steps_completed": self._step_count}
            )

        # Check time limit
        elapsed = time.time() - self._start_time
        if elapsed >= self.max_runtime_seconds:
            return ExitStatus(
                should_exit=True,
                reason=ExitReason.MAX_TIME_REACHED,
                message=f"Reached maximum runtime ({self.max_runtime_seconds}s)",
                details={"elapsed_seconds": elapsed}
            )

        # Check rate limit
        if rate_limit_remaining:
            hourly, minutely = rate_limit_remaining
            if hourly <= 0:
                return ExitStatus(
                    should_exit=True,
                    reason=ExitReason.RATE_LIMIT_EXHAUSTED,
                    message="Hourly rate limit exhausted"
                )

        # Check plan completion
        if plan_remaining == 0 and self._step_count > 0:
            return ExitStatus(
                should_exit=True,
                reason=ExitReason.ALL_STEPS_DONE,
                message="All planned steps completed",
                details={
                    "steps_completed": self._step_count,
                    "tasks": self._completed_tasks
                }
            )

        # Check completion signals in response
        if agent_response and self._check_completion_signals(agent_response):
            return ExitStatus(
                should_exit=True,
                reason=ExitReason.TASK_COMPLETE,
                message="Agent signaled task completion",
                details={"response_snippet": agent_response[:200]}
            )

        # No exit condition met
        return ExitStatus(
            should_exit=False,
            reason=ExitReason.NOT_EXITED,
            message="Continuing execution",
            details={
                "step_count": self._step_count,
                "elapsed_seconds": elapsed,
                "plan_remaining": plan_remaining
            }
        )

    def get_progress(self) -> dict:
        """Get current progress information."""
        elapsed = time.time() - self._start_time
        return {
            "steps_completed": self._step_count,
            "max_steps": self.max_steps,
            "elapsed_seconds": round(elapsed, 1),
            "max_runtime_seconds": self.max_runtime_seconds,
            "consecutive_failures": self._consecutive_failures,
            "max_consecutive_failures": self.max_consecutive_failures,
            "completed_tasks": self._completed_tasks,
            "progress_percent": round(
                min(100, (self._step_count / self.max_steps) * 100), 1
            ) if self.max_steps > 0 else 0
        }


class MetaVerdictChecker:
    """
    Checks meta agent verdicts for final approval.
    """

    def __init__(self):
        self._approval_keywords = ["pass", "approve", "approved", "accept", "accepted"]
        self._rejection_keywords = ["block", "reject", "rejected", "fail", "failed", "deny", "denied"]

    def check_verdict(self, verdict: dict) -> ExitStatus:
        """
        Check meta agent verdict.

        Args:
            verdict: Meta agent response dict

        Returns:
            ExitStatus based on verdict
        """
        status = verdict.get("verdict", verdict.get("status", "")).lower()

        # Check for explicit approval
        if any(kw in status for kw in self._approval_keywords):
            return ExitStatus(
                should_exit=True,
                reason=ExitReason.TASK_COMPLETE,
                message="Meta agent approved changes",
                details=verdict
            )

        # Check for rejection
        if any(kw in status for kw in self._rejection_keywords):
            return ExitStatus(
                should_exit=True,
                reason=ExitReason.META_REJECTED,
                message=f"Meta agent rejected: {verdict.get('reason', 'No reason given')}",
                details=verdict
            )

        # Check for error
        if "error" in status:
            return ExitStatus(
                should_exit=False,  # Don't exit on error, let retry handle it
                reason=ExitReason.NOT_EXITED,
                message="Meta agent encountered error",
                details=verdict
            )

        # Unknown verdict - don't exit
        return ExitStatus(
            should_exit=False,
            reason=ExitReason.NOT_EXITED,
            message=f"Unknown meta verdict: {status}",
            details=verdict
        )
