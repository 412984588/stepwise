"""Unit tests for rate limiter service."""

import time
import pytest

from backend.services.rate_limiter import RateLimiter, RateLimitConfig


class TestRateLimiterBasic:
    """Test basic rate limiter functionality."""

    def test_allows_requests_under_limit(self) -> None:
        """Requests under the limit should be allowed."""
        limiter = RateLimiter(RateLimitConfig(max_requests=5, window_seconds=60))

        for i in range(5):
            assert limiter.is_allowed("client1") is True

    def test_blocks_requests_over_limit(self) -> None:
        """Requests over the limit should be blocked."""
        limiter = RateLimiter(RateLimitConfig(max_requests=3, window_seconds=60))

        # First 3 requests should be allowed
        for i in range(3):
            assert limiter.is_allowed("client1") is True

        # 4th request should be blocked
        assert limiter.is_allowed("client1") is False

    def test_different_clients_have_separate_limits(self) -> None:
        """Different clients should have independent rate limits."""
        limiter = RateLimiter(RateLimitConfig(max_requests=2, window_seconds=60))

        # Client 1 uses their quota
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is False

        # Client 2 should still be able to make requests
        assert limiter.is_allowed("client2") is True
        assert limiter.is_allowed("client2") is True
        assert limiter.is_allowed("client2") is False


class TestRateLimiterSlidingWindow:
    """Test sliding window behavior."""

    def test_old_requests_are_removed_from_window(self) -> None:
        """Requests outside the window should not count toward limit."""
        limiter = RateLimiter(RateLimitConfig(max_requests=2, window_seconds=1))

        # Make 2 requests (hit limit)
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is False

        # Wait for window to pass
        time.sleep(1.1)

        # Should be able to make requests again
        assert limiter.is_allowed("client1") is True

    def test_partial_window_reset(self) -> None:
        """Only requests outside window should be removed."""
        limiter = RateLimiter(RateLimitConfig(max_requests=3, window_seconds=2))

        # Make 2 requests
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True

        # Wait 1 second
        time.sleep(1.1)

        # Make 1 more request (total 3, at limit)
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is False  # Should be blocked

        # Wait another second (first 2 requests should expire)
        time.sleep(1.1)

        # Should be able to make 2 more requests
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True


class TestRateLimiterGetRemaining:
    """Test get_remaining method."""

    def test_get_remaining_starts_at_max(self) -> None:
        """Remaining should start at max_requests."""
        limiter = RateLimiter(RateLimitConfig(max_requests=5, window_seconds=60))

        assert limiter.get_remaining("client1") == 5

    def test_get_remaining_decreases_with_requests(self) -> None:
        """Remaining should decrease as requests are made."""
        limiter = RateLimiter(RateLimitConfig(max_requests=5, window_seconds=60))

        limiter.is_allowed("client1")
        assert limiter.get_remaining("client1") == 4

        limiter.is_allowed("client1")
        assert limiter.get_remaining("client1") == 3

    def test_get_remaining_never_negative(self) -> None:
        """Remaining should not go below zero."""
        limiter = RateLimiter(RateLimitConfig(max_requests=2, window_seconds=60))

        limiter.is_allowed("client1")
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")  # Blocked but still tracked

        assert limiter.get_remaining("client1") == 0


class TestRateLimiterGetRetryAfter:
    """Test get_retry_after method."""

    def test_get_retry_after_zero_when_not_limited(self) -> None:
        """Retry after should be 0 when not rate limited."""
        limiter = RateLimiter(RateLimitConfig(max_requests=5, window_seconds=60))

        limiter.is_allowed("client1")
        assert limiter.get_retry_after("client1") == 0

    def test_get_retry_after_when_rate_limited(self) -> None:
        """Retry after should return seconds until window resets."""
        limiter = RateLimiter(RateLimitConfig(max_requests=2, window_seconds=5))

        # Hit the limit
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")

        # Should need to wait ~5 seconds
        retry_after = limiter.get_retry_after("client1")
        assert 4 <= retry_after <= 6  # Allow some timing variance

    def test_get_retry_after_decreases_over_time(self) -> None:
        """Retry after should decrease as time passes."""
        limiter = RateLimiter(RateLimitConfig(max_requests=2, window_seconds=3))

        # Hit the limit
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")

        retry_after_1 = limiter.get_retry_after("client1")

        # Wait a bit
        time.sleep(1)

        retry_after_2 = limiter.get_retry_after("client1")

        # Should be less time to wait
        assert retry_after_2 < retry_after_1


class TestRateLimiterReset:
    """Test reset functionality."""

    def test_reset_single_client(self) -> None:
        """Reset should clear rate limit for specific client."""
        limiter = RateLimiter(RateLimitConfig(max_requests=2, window_seconds=60))

        # Hit limit for client1
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")
        assert limiter.is_allowed("client1") is False

        # Reset client1
        limiter.reset("client1")

        # Should be able to make requests again
        assert limiter.is_allowed("client1") is True

    def test_reset_all_clients(self) -> None:
        """Reset with no client_id should clear all limits."""
        limiter = RateLimiter(RateLimitConfig(max_requests=2, window_seconds=60))

        # Hit limits for multiple clients
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")
        limiter.is_allowed("client2")
        limiter.is_allowed("client2")

        assert limiter.is_allowed("client1") is False
        assert limiter.is_allowed("client2") is False

        # Reset all
        limiter.reset()

        # All clients should be able to make requests
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client2") is True

    def test_reset_nonexistent_client_does_not_error(self) -> None:
        """Resetting non-existent client should not raise error."""
        limiter = RateLimiter(RateLimitConfig(max_requests=5, window_seconds=60))

        # Should not raise
        limiter.reset("nonexistent_client")


class TestRateLimiterConcurrency:
    """Test thread safety (basic smoke test)."""

    def test_concurrent_requests_do_not_exceed_limit(self) -> None:
        """Concurrent requests should still respect the limit."""
        import threading

        limiter = RateLimiter(RateLimitConfig(max_requests=10, window_seconds=60))
        results = []

        def make_request():
            results.append(limiter.is_allowed("client1"))

        # Make 15 concurrent requests
        threads = [threading.Thread(target=make_request) for _ in range(15)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exactly 10 should be allowed
        assert sum(results) == 10
