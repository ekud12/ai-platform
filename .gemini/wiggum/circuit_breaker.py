#!/usr/bin/env python3
"""
Circuit breaker pattern implementation for Wiggum.

Prevents cascading failures by stopping requests when
too many consecutive failures occur.
"""

import time
import threading
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable, TypeVar, Generic

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation, requests flow through
    OPEN = "open"          # Failing, requests are blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitStats:
    """Statistics about circuit breaker."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    consecutive_failures: int = 0
    state: CircuitState = CircuitState.CLOSED
    last_failure_time: Optional[float] = None
    last_state_change: Optional[float] = None


class CircuitBreakerError(Exception):
    """Raised when circuit is open and request is rejected."""
    pass


class CircuitBreaker:
    """
    Circuit breaker for API calls.

    States:
    - CLOSED: Normal operation. Track failures.
    - OPEN: Too many failures. Reject all requests.
    - HALF_OPEN: After timeout, allow one request to test recovery.

    Usage:
        breaker = CircuitBreaker(max_failures=5)

        try:
            result = breaker.call(lambda: api_request())
        except CircuitBreakerError:
            print("Circuit is open, request rejected")
    """

    def __init__(
        self,
        max_failures: int = 5,
        reset_timeout: float = 60.0,
        half_open_max_calls: int = 1
    ):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0

        self._lock = threading.Lock()
        self._stats = CircuitStats()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            self._check_state_transition()
            return self._state

    def _check_state_transition(self):
        """Check if state should transition based on timeout."""
        if self._state == CircuitState.OPEN:
            if self._last_failure_time:
                elapsed = time.time() - self._last_failure_time
                if elapsed >= self.reset_timeout:
                    self._transition_to(CircuitState.HALF_OPEN)

    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state."""
        old_state = self._state
        self._state = new_state
        self._stats.state = new_state
        self._stats.last_state_change = time.time()

        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0

        if new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0

    def _record_success(self):
        """Record a successful call."""
        self._stats.total_calls += 1
        self._stats.successful_calls += 1
        self._stats.consecutive_failures = 0

        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.half_open_max_calls:
                self._transition_to(CircuitState.CLOSED)
        else:
            self._failure_count = 0

    def _record_failure(self):
        """Record a failed call."""
        self._stats.total_calls += 1
        self._stats.failed_calls += 1
        self._stats.consecutive_failures += 1
        self._last_failure_time = time.time()
        self._stats.last_failure_time = self._last_failure_time

        self._failure_count += 1

        if self._state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)
        elif self._failure_count >= self.max_failures:
            self._transition_to(CircuitState.OPEN)

    def can_execute(self) -> bool:
        """Check if a call can be executed."""
        with self._lock:
            self._check_state_transition()

            if self._state == CircuitState.CLOSED:
                return True

            if self._state == CircuitState.OPEN:
                return False

            if self._state == CircuitState.HALF_OPEN:
                return self._half_open_calls < self.half_open_max_calls

            return False

    def call(self, func: Callable[[], T], fallback: Optional[Callable[[], T]] = None) -> T:
        """
        Execute a function through the circuit breaker.

        Args:
            func: Function to execute
            fallback: Optional fallback function if circuit is open

        Returns:
            Result of func or fallback

        Raises:
            CircuitBreakerError: If circuit is open and no fallback provided
        """
        with self._lock:
            self._check_state_transition()

            if self._state == CircuitState.OPEN:
                self._stats.rejected_calls += 1
                if fallback:
                    return fallback()
                raise CircuitBreakerError(
                    f"Circuit is open. {self.max_failures} consecutive failures. "
                    f"Will retry in {self.reset_timeout - (time.time() - (self._last_failure_time or 0)):.1f}s"
                )

            if self._state == CircuitState.HALF_OPEN:
                self._half_open_calls += 1

        # Execute outside lock
        try:
            result = func()
            with self._lock:
                self._record_success()
            return result

        except Exception as e:
            with self._lock:
                self._record_failure()
            raise

    def get_stats(self) -> CircuitStats:
        """Get circuit breaker statistics."""
        with self._lock:
            self._check_state_transition()
            return CircuitStats(
                total_calls=self._stats.total_calls,
                successful_calls=self._stats.successful_calls,
                failed_calls=self._stats.failed_calls,
                rejected_calls=self._stats.rejected_calls,
                consecutive_failures=self._failure_count,
                state=self._state,
                last_failure_time=self._last_failure_time,
                last_state_change=self._stats.last_state_change
            )

    def reset(self):
        """Manually reset the circuit breaker."""
        with self._lock:
            self._transition_to(CircuitState.CLOSED)
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._stats = CircuitStats()


class RetryWithCircuitBreaker:
    """
    Combines retry logic with circuit breaker.

    Retries failed calls with exponential backoff,
    but stops if circuit breaker opens.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        circuit_breaker: Optional[CircuitBreaker] = None
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.circuit_breaker = circuit_breaker or CircuitBreaker()

    def execute(
        self,
        func: Callable[[], T],
        is_retriable: Optional[Callable[[Exception], bool]] = None
    ) -> T:
        """
        Execute a function with retries and circuit breaker protection.

        Args:
            func: Function to execute
            is_retriable: Optional function to check if exception is retriable

        Returns:
            Result of func

        Raises:
            Last exception if all retries exhausted
            CircuitBreakerError if circuit opens
        """
        last_exception: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                return self.circuit_breaker.call(func)

            except CircuitBreakerError:
                raise

            except Exception as e:
                last_exception = e

                # Check if retriable
                if is_retriable and not is_retriable(e):
                    raise

                # Check if more retries available
                if attempt >= self.max_retries:
                    raise

                # Calculate delay with exponential backoff
                delay = min(
                    self.base_delay * (2 ** attempt),
                    self.max_delay
                )

                time.sleep(delay)

        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected state in RetryWithCircuitBreaker")
