"""Contract tests for API key protection on stats and reports endpoints."""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import HintSession, Problem, ProblemType, HintLayer, SessionStatus
from backend.utils.validation import generate_session_id


@pytest.mark.contract
class TestStatsEndpointsAPIKeyProtection:
    """Test that stats endpoints require API key when configured."""

    def test_stats_summary_without_api_key_when_required(
        self, client: TestClient, monkeypatch
    ) -> None:
        """Stats summary returns 401 when API key is configured but not provided."""
        monkeypatch.setenv("API_ACCESS_KEY", "test-secret-key")

        response = client.get("/api/v1/stats/summary")

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "API_KEY_MISSING"

    def test_stats_summary_with_invalid_api_key(self, client: TestClient, monkeypatch) -> None:
        """Stats summary returns 401 with invalid API key."""
        monkeypatch.setenv("API_ACCESS_KEY", "test-secret-key")

        response = client.get(
            "/api/v1/stats/summary",
            headers={"X-API-Key": "wrong-key"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "API_KEY_INVALID"

    def test_stats_summary_with_valid_api_key(self, client: TestClient, monkeypatch) -> None:
        """Stats summary returns 200 with valid API key."""
        monkeypatch.setenv("API_ACCESS_KEY", "test-secret-key")

        response = client.get(
            "/api/v1/stats/summary",
            headers={"X-API-Key": "test-secret-key"},
        )

        assert response.status_code == 200

    def test_stats_summary_without_api_key_when_not_required(
        self, client: TestClient, monkeypatch
    ) -> None:
        """Stats summary allows access when API key is not configured."""
        monkeypatch.delenv("API_ACCESS_KEY", raising=False)

        response = client.get("/api/v1/stats/summary")

        assert response.status_code == 200

    def test_stats_dashboard_is_public(self, client: TestClient, monkeypatch) -> None:
        """Stats dashboard is public and returns 200 without API key."""
        monkeypatch.setenv("API_ACCESS_KEY", "test-secret-key")

        response = client.get("/api/v1/stats/dashboard")

        assert response.status_code == 200

    def test_stats_dashboard_works_with_api_key(self, client: TestClient, monkeypatch) -> None:
        """Stats dashboard returns 200 with or without API key."""
        monkeypatch.setenv("API_ACCESS_KEY", "test-secret-key")

        response = client.get(
            "/api/v1/stats/dashboard",
            headers={"X-API-Key": "test-secret-key"},
        )

        assert response.status_code == 200


@pytest.mark.contract
class TestReportsEndpointsAPIKeyProtection:
    """Test that reports endpoints require proper authentication (session tokens for PDF, API key for summary)."""

    def test_pdf_report_without_session_token(self, client: TestClient, test_db: Session) -> None:
        """PDF report returns 403 when session access token is missing."""
        # Create a test session with access token
        session_id = generate_session_id()
        access_token = HintSession.generate_access_token()
        problem = Problem(
            raw_text="Solve 2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        session = HintSession(
            id=session_id,
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            status=SessionStatus.COMPLETED,
            session_access_token=access_token,
        )
        test_db.add(session)
        test_db.commit()

        # Call without token
        response = client.get(f"/api/v1/reports/session/{session_id}/pdf")

        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "MISSING_SESSION_TOKEN"

    def test_pdf_report_with_invalid_session_token(
        self, client: TestClient, test_db: Session
    ) -> None:
        """PDF report returns 403 with invalid session access token."""
        # Create a test session with access token
        session_id = generate_session_id()
        access_token = HintSession.generate_access_token()
        problem = Problem(
            raw_text="Solve 2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        session = HintSession(
            id=session_id,
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            status=SessionStatus.COMPLETED,
            session_access_token=access_token,
        )
        test_db.add(session)
        test_db.commit()

        # Call with wrong token
        response = client.get(
            f"/api/v1/reports/session/{session_id}/pdf",
            headers={"X-Session-Access-Token": "wrong-token-12345678"},
        )

        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "INVALID_SESSION_TOKEN"

    def test_pdf_report_with_valid_session_token(
        self, client: TestClient, test_db: Session
    ) -> None:
        """PDF report returns 200 with valid session access token."""
        # Create a test session with access token
        session_id = generate_session_id()
        access_token = HintSession.generate_access_token()
        problem = Problem(
            raw_text="Solve 2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        session = HintSession(
            id=session_id,
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            status=SessionStatus.COMPLETED,
            session_access_token=access_token,
        )
        test_db.add(session)
        test_db.commit()

        # Call with correct token
        response = client.get(
            f"/api/v1/reports/session/{session_id}/pdf",
            headers={"X-Session-Access-Token": access_token},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_session_summary_requires_api_key(
        self, client: TestClient, test_db: Session, monkeypatch
    ) -> None:
        """Session summary returns 401 when API key is configured but not provided."""
        monkeypatch.setenv("API_ACCESS_KEY", "test-secret-key")

        # Create a test session
        session_id = generate_session_id()
        problem = Problem(
            raw_text="Solve 2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        session = HintSession(
            id=session_id,
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            status=SessionStatus.COMPLETED,
        )
        test_db.add(session)
        test_db.commit()

        response = client.get(f"/api/v1/reports/session/{session_id}/summary")

        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "API_KEY_MISSING"

    def test_session_summary_with_valid_api_key(
        self, client: TestClient, test_db: Session, monkeypatch
    ) -> None:
        """Session summary returns 200 with valid API key."""
        monkeypatch.setenv("API_ACCESS_KEY", "test-secret-key")

        # Create a test session
        session_id = generate_session_id()
        problem = Problem(
            raw_text="Solve 2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        session = HintSession(
            id=session_id,
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            status=SessionStatus.COMPLETED,
        )
        test_db.add(session)
        test_db.commit()

        response = client.get(
            f"/api/v1/reports/session/{session_id}/summary",
            headers={"X-API-Key": "test-secret-key"},
        )

        assert response.status_code == 200


@pytest.mark.contract
class TestSessionEndpointsNotProtected:
    """Test that core learning flow endpoints remain accessible without API key."""

    def test_start_session_does_not_require_api_key(self, client: TestClient, monkeypatch) -> None:
        """Session start is accessible without API key."""
        monkeypatch.setenv("API_ACCESS_KEY", "test-secret-key")

        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 2x + 5 = 11"},
        )

        assert response.status_code == 201

    def test_respond_to_hint_does_not_require_api_key(
        self, client: TestClient, monkeypatch
    ) -> None:
        """Responding to hints is accessible without API key."""
        monkeypatch.setenv("API_ACCESS_KEY", "test-secret-key")

        # First create a session
        start_response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 2x + 5 = 11"},
        )
        session_id = start_response.json()["session_id"]

        # Then respond without API key
        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "移项，等式两边同时减5"},
        )

        assert response.status_code == 200
