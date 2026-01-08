#!/usr/bin/env python3
"""
Rate limiting for Wiggum API calls.

Implements token bucket algorithm with configurable rates
for hourly and per-minute limits.
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Optional
from collections import deque


@dataclass
class RateLimitStats:
    """Statistics about rate limiting."""
    total_calls: int = 0
    calls_this_hour: int = 0
    calls_this_minute: int = 0
    total_wait_time: float = 0.0
    times_limited: int = 0


class RateLimiter:
    """
    Rate limiter using sliding window algorithm.

    Supports:
    - Per-hour limits (default: 100)
    - Per-minute limits (default: 10)
    - Configurable cooldown periods
    """

    def __init__(
        self,
        max_per_hour: int = 100,
        max_per_minute: int = 10,
        cooldown_seconds: int = 60
    ):
        self.max_per_hour = max_per_hour
        self.max_per_minute = max_per_minute
        self.cooldown_seconds = cooldown_seconds

        # Sliding windows
        self._hour_window: deque[float] = deque()
        self._minute_window: deque[float] = deque()

        # Thread safety
        self._lock = threading.Lock()

        # Stats
        self.stats = RateLimitStats()

    def _cleanup_windows(self, now: float):
        """Remove expired entries from sliding windows."""
        hour_ago = now - 3600
        minute_ago = now - 60

        while self._hour_window and self._hour_window[0] < hour_ago:
            self._hour_window.popleft()

        while self._minute_window and self._minute_window[0] < minute_ago:
            self._minute_window.popleft()

    def _calculate_wait_time(self, now: float) -> float:
        """Calculate how long to wait before next call is allowed."""
        self._cleanup_windows(now)

        wait_time = 0.0

        # Check hourly limit
        if len(self._hour_window) >= self.max_per_hour:
            oldest_hour = self._hour_window[0]
            wait_for_hour = (oldest_hour + 3600) - now
            wait_time = max(wait_time, wait_for_hour)

        # Check minute limit
        if len(self._minute_window) >= self.max_per_minute:
            oldest_minute = self._minute_window[0]
            wait_for_minute = (oldest_minute + 60) - now
            wait_time = max(wait_time, wait_for_minute)

        return max(0.0, wait_time)

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission to make an API call.

        Args:
            timeout: Maximum time to wait (None = wait indefinitely)

        Returns:
            True if acquired, False if timed out
        """
        start_time = time.time()

        with self._lock:
            while True:
                now = time.time()
                wait_time = self._calculate_wait_time(now)

                if wait_time <= 0:
                    # Can proceed
                    self._hour_window.append(now)
                    self._minute_window.append(now)
                    self.stats.total_calls += 1
                    return True

                # Check timeout
                elapsed = now - start_time
                if timeout is not None and elapsed + wait_time > timeout:
                    return False

                # Record stats
                self.stats.times_limited += 1

                # Release lock while waiting
                self._lock.release()
                try:
                    actual_wait = min(wait_time, 1.0)  # Check every second
                    time.sleep(actual_wait)
                    self.stats.total_wait_time += actual_wait
                finally:
                    self._lock.acquire()

    def get_stats(self) -> RateLimitStats:
        """Get current rate limiting statistics."""
        with self._lock:
            now = time.time()
            self._cleanup_windows(now)

            self.stats.calls_this_hour = len(self._hour_window)
            self.stats.calls_this_minute = len(self._minute_window)

            return self.stats

    def get_remaining(self) -> tuple[int, int]:
        """
        Get remaining calls allowed.

        Returns:
            Tuple of (remaining_this_hour, remaining_this_minute)
        """
        with self._lock:
            now = time.time()
            self._cleanup_windows(now)

            remaining_hour = max(0, self.max_per_hour - len(self._hour_window))
            remaining_minute = max(0, self.max_per_minute - len(self._minute_window))

            return remaining_hour, remaining_minute

    def wait_if_needed(self) -> float:
        """
        Wait if rate limited, return time waited.

        Returns:
            Time waited in seconds
        """
        start = time.time()
        self.acquire()
        return time.time() - start

    def reset(self):
        """Reset rate limiter state."""
        with self._lock:
            self._hour_window.clear()
            self._minute_window.clear()
            self.stats = RateLimitStats()


class AdaptiveRateLimiter(RateLimiter):
    """
    Rate limiter that adapts based on API responses.

    Automatically backs off when receiving rate limit errors
    and speeds up when requests are successful.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._backoff_factor = 1.0
        self._consecutive_successes = 0
        self._consecutive_failures = 0

    def record_success(self):
        """Record a successful API call."""
        with self._lock:
            self._consecutive_successes += 1
            self._consecutive_failures = 0

            # Speed up after 10 consecutive successes
            if self._consecutive_successes >= 10:
                self._backoff_factor = max(0.5, self._backoff_factor * 0.9)
                self._consecutive_successes = 0

    def record_failure(self, is_rate_limit: bool = False):
        """Record a failed API call."""
        with self._lock:
            self._consecutive_failures += 1
            self._consecutive_successes = 0

            if is_rate_limit:
                # Aggressive backoff for rate limit errors
                self._backoff_factor = min(4.0, self._backoff_factor * 2.0)
            else:
                # Mild backoff for other errors
                self._backoff_factor = min(2.0, self._backoff_factor * 1.2)

    def _calculate_wait_time(self, now: float) -> float:
        """Calculate wait time with backoff factor applied."""
        base_wait = super()._calculate_wait_time(now)
        return base_wait * self._backoff_factor
