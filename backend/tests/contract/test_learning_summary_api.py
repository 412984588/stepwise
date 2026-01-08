"""Contract tests for learning summary API endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.contract
class TestLearningSummaryAPI:
    """Test learning summary API endpoint (requires API key)."""

    def test_get_summary_returns_200(
        self, client: TestClient, api_key_headers: dict[str, str]
    ) -> None:
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 2x + 5 = 11", "locale": "en-US", "grade_level": 7},
        )
        session_id = response.json()["session_id"]

        response = client.get(
            f"/api/v1/reports/session/{session_id}/summary", headers=api_key_headers
        )

        assert response.status_code == 200

    def test_summary_has_required_fields(
        self, client: TestClient, api_key_headers: dict[str, str]
    ) -> None:
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Calculate 15 + 27", "locale": "en-US", "grade_level": 5},
        )
        session_id = response.json()["session_id"]

        response = client.get(
            f"/api/v1/reports/session/{session_id}/summary", headers=api_key_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "headline" in data
        assert "performance_level" in data
        assert "insights" in data
        assert "recommendation" in data

        assert isinstance(data["headline"], str)
        assert isinstance(data["performance_level"], str)
        assert isinstance(data["insights"], list)
        assert isinstance(data["recommendation"], str)

    def test_summary_performance_levels_valid(
        self, client: TestClient, api_key_headers: dict[str, str]
    ) -> None:
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve x + 3 = 7", "locale": "en-US", "grade_level": 6},
        )
        session_id = response.json()["session_id"]

        response = client.get(
            f"/api/v1/reports/session/{session_id}/summary", headers=api_key_headers
        )

        data = response.json()
        assert data["performance_level"] in ["Excellent", "Good", "Needs Practice"]

    def test_summary_insights_not_empty(
        self, client: TestClient, api_key_headers: dict[str, str]
    ) -> None:
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "What is 10 * 5?", "locale": "en-US", "grade_level": 4},
        )
        session_id = response.json()["session_id"]

        response = client.get(
            f"/api/v1/reports/session/{session_id}/summary", headers=api_key_headers
        )

        data = response.json()
        assert len(data["insights"]) > 0
        assert all(isinstance(insight, str) for insight in data["insights"])

    def test_summary_after_completion(
        self, client: TestClient, api_key_headers: dict[str, str]
    ) -> None:
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 3x = 12", "locale": "en-US", "grade_level": 6},
        )
        session_id = response.json()["session_id"]

        client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "I understand this is a linear equation"},
        )
        client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "I will divide both sides by 3"},
        )
        client.post(f"/api/v1/sessions/{session_id}/complete")

        response = client.get(
            f"/api/v1/reports/session/{session_id}/summary", headers=api_key_headers
        )

        data = response.json()
        assert (
            "independently" in data["insights"][0].lower()
            or "completed" in data["insights"][0].lower()
        )

    def test_summary_nonexistent_session_404(
        self, client: TestClient, api_key_headers: dict[str, str]
    ) -> None:
        response = client.get(
            "/api/v1/reports/session/nonexistent/summary", headers=api_key_headers
        )

        assert response.status_code == 404
        assert response.json()["error"] == "SESSION_NOT_FOUND"

    def test_summary_requires_api_key(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve x = 5", "locale": "en-US", "grade_level": 5},
        )
        session_id = response.json()["session_id"]

        response = client.get(f"/api/v1/reports/session/{session_id}/summary")
        assert response.status_code == 401
