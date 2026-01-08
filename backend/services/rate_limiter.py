"""In-memory rate limiter service for API endpoints."""

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, Deque


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    max_requests: int = 20  # Maximum requests
    window_seconds: int = 60  # Time window in seconds


class RateLimiter:
    """
    In-memory sliding window rate limiter.

    Tracks requests per client identifier (IP or session_id) within a time window.
    Thread-safe using locks.
    """

    def __init__(self, config: RateLimitConfig | None = None):
        """
        Initialize rate limiter.

        Args:
            config: Rate limit configuration (defaults to 20 requests per 60 seconds)
        """
        self.config = config or RateLimitConfig()
        self._requests: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def is_allowed(self, client_id: str) -> bool:
        """
        Check if a request from client_id is allowed.

        Args:
            client_id: Unique identifier for the client (IP address or session_id)

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        with self._lock:
            now = time.time()
            window_start = now - self.config.window_seconds

            # Get request timestamps for this client
            requests = self._requests[client_id]

            # Remove timestamps outside the current window
            while requests and requests[0] < window_start:
                requests.popleft()

            # Check if client has exceeded limit
            if len(requests) >= self.config.max_requests:
                return False

            # Record this request
            requests.append(now)
            return True

    def get_remaining(self, client_id: str) -> int:
        """
        Get remaining requests for client_id.

        Args:
            client_id: Unique identifier for the client

        Returns:
            Number of remaining requests in current window
        """
        with self._lock:
            now = time.time()
            window_start = now - self.config.window_seconds

            requests = self._requests[client_id]

            # Remove old timestamps
            while requests and requests[0] < window_start:
                requests.popleft()

            return max(0, self.config.max_requests - len(requests))

    def get_retry_after(self, client_id: str) -> int:
        """
        Get seconds until client_id can make another request.

        Args:
            client_id: Unique identifier for the client

        Returns:
            Seconds until rate limit resets (0 if not rate limited)
        """
        with self._lock:
            now = time.time()
            window_start = now - self.config.window_seconds

            requests = self._requests[client_id]

            # Remove old timestamps
            while requests and requests[0] < window_start:
                requests.popleft()

            # If not rate limited, return 0
            if len(requests) < self.config.max_requests:
                return 0

            # Time until oldest request exits the window
            oldest_request = requests[0]
            retry_after = int(oldest_request + self.config.window_seconds - now) + 1
            return max(0, retry_after)

    def reset(self, client_id: str | None = None) -> None:
        """
        Reset rate limit for a client or all clients.

        Args:
            client_id: Client to reset, or None to reset all
        """
        with self._lock:
            if client_id is None:
                self._requests.clear()
            elif client_id in self._requests:
                del self._requests[client_id]


# Global rate limiter instances
_stats_limiter = RateLimiter(RateLimitConfig(max_requests=20, window_seconds=60))
_reports_limiter = RateLimiter(RateLimitConfig(max_requests=20, window_seconds=60))


def get_stats_rate_limiter() -> RateLimiter:
    """Get the global stats rate limiter instance."""
    return _stats_limiter


def get_reports_rate_limiter() -> RateLimiter:
    """Get the global reports rate limiter instance."""
    return _reports_limiter
