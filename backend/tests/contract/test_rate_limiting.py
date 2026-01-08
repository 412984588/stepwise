"""Contract tests for rate limiting behavior and Retry-After headers."""

import os

import pytest
from fastapi.testclient import TestClient

from backend.main import app


class TestRateLimitRetryAfterHeader:
    """Test that 429 responses include Retry-After header."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def api_key(self):
        """Get API key from environment or use test key."""
        return os.getenv("API_ACCESS_KEY", "test_api_key")

    @pytest.mark.contract
    def test_stats_dashboard_rate_limit_includes_retry_after_header(
        self, client: TestClient, api_key: str
    ) -> None:
        """Test that stats dashboard returns Retry-After header when rate limited."""
        # Make requests until rate limit is hit (20 requests/60 seconds, so 21 should trigger)
        for i in range(25):
            response = client.get("/api/v1/stats/dashboard", headers={"X-API-Key": api_key})
            if response.status_code == 429:
                # Verify 429 response includes Retry-After header
                assert "Retry-After" in response.headers
                retry_after = int(response.headers["Retry-After"])
                assert retry_after > 0
                assert retry_after <= 60  # Should be within window size

                # Verify response body includes retry_after (flattened by exception handler)
                data = response.json()
                assert "retry_after" in data
                assert data["retry_after"] == retry_after
                return  # Success

        pytest.fail("Rate limit not triggered after 25 requests")

    @pytest.mark.contract
    def test_stats_summary_rate_limit_includes_retry_after_header(
        self, client: TestClient, api_key: str
    ) -> None:
        """Test that stats summary returns Retry-After header when rate limited."""
        # Make requests until rate limit is hit (20 requests/60 seconds, so 21 should trigger)
        for i in range(25):
            response = client.get("/api/v1/stats/summary", headers={"X-API-Key": api_key})
            if response.status_code == 429:
                # Verify 429 response includes Retry-After header
                assert "Retry-After" in response.headers
                retry_after = int(response.headers["Retry-After"])
                assert retry_after > 0
                assert retry_after <= 60  # Should be within window size

                # Verify response body includes retry_after (flattened by exception handler)
                data = response.json()
                assert "retry_after" in data
                assert data["retry_after"] == retry_after
                return  # Success

        pytest.fail("Rate limit not triggered after 25 requests")

    @pytest.mark.contract
    def test_retry_after_header_format_is_valid(self, client: TestClient, api_key: str) -> None:
        """Test that Retry-After header contains a valid integer."""
        # Trigger rate limit (20 requests/60 seconds, so 21 should trigger)
        for i in range(25):
            response = client.get("/api/v1/stats/dashboard", headers={"X-API-Key": api_key})
            if response.status_code == 429:
                # Verify header is a valid integer
                retry_after_str = response.headers.get("Retry-After")
                assert retry_after_str is not None
                assert retry_after_str.isdigit()

                retry_after_int = int(retry_after_str)
                assert retry_after_int > 0
                return  # Success

        pytest.fail("Rate limit not triggered after 25 requests")

    @pytest.mark.contract
    def test_retry_after_header_matches_body(self, client: TestClient, api_key: str) -> None:
        """Test that Retry-After header matches retry_after in response body."""
        # Trigger rate limit (20 requests/60 seconds, so 21 should trigger)
        for i in range(25):
            response = client.get("/api/v1/stats/dashboard", headers={"X-API-Key": api_key})
            if response.status_code == 429:
                # Verify header and body match (body is flattened by exception handler)
                assert "Retry-After" in response.headers
                header_value = int(response.headers["Retry-After"])
                body_value = response.json()["retry_after"]
                assert header_value == body_value
                return  # Success

        pytest.fail("Rate limit not triggered after 25 requests")
