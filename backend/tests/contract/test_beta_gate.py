"""Contract tests for beta access code gate on session endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import HintSession, Problem, ProblemType, HintLayer, SessionStatus
from backend.utils.validation import generate_session_id


@pytest.mark.contract
class TestBetaGateDisabled:
    """Test that endpoints work normally when BETA_ACCESS_CODE is not set."""

    def test_start_session_without_beta_code_when_gate_disabled(
        self, client: TestClient, monkeypatch
    ) -> None:
        """Session start works without beta code when gate is disabled."""
        monkeypatch.delenv("BETA_ACCESS_CODE", raising=False)

        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 2x + 5 = 11"},
        )

        assert response.status_code == 201

    def test_respond_without_beta_code_when_gate_disabled(
        self, client: TestClient, monkeypatch
    ) -> None:
        """Responding to hints works without beta code when gate is disabled."""
        monkeypatch.delenv("BETA_ACCESS_CODE", raising=False)

        # First create a session
        start_response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 2x + 5 = 11"},
        )
        session_id = start_response.json()["session_id"]

        # Then respond without beta code
        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "I understand we need to isolate x by moving terms"},
        )

        assert response.status_code == 200


@pytest.mark.contract
class TestBetaGateMissingCode:
    """Test that endpoints return 403 when beta code is required but missing."""

    def test_start_session_missing_beta_code(self, client: TestClient, monkeypatch) -> None:
        """Session start returns 403 when beta code is required but missing."""
        monkeypatch.setenv("BETA_ACCESS_CODE", "beta-secret-123")

        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 2x + 5 = 11"},
        )

        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "BETA_CODE_REQUIRED"
        assert "beta" in data["message"].lower()

    def test_respond_missing_beta_code(
        self, client: TestClient, test_db: Session, monkeypatch
    ) -> None:
        """Responding to hints returns 403 when beta code is required but missing."""
        # Create session directly in DB to bypass beta gate for setup
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
            current_layer=HintLayer.CONCEPT,
            status=SessionStatus.ACTIVE,
        )
        test_db.add(session)
        test_db.commit()

        # Now enable beta gate and try to respond
        monkeypatch.setenv("BETA_ACCESS_CODE", "beta-secret-123")

        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "I understand we need to isolate x by moving terms"},
        )

        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "BETA_CODE_REQUIRED"

    def test_reveal_missing_beta_code(
        self, client: TestClient, test_db: Session, monkeypatch
    ) -> None:
        """Reveal solution returns 403 when beta code is required but missing."""
        # Create session at STEP layer to allow reveal
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
            current_layer=HintLayer.STEP,
            status=SessionStatus.ACTIVE,
        )
        test_db.add(session)
        test_db.commit()

        # Enable beta gate and try to reveal
        monkeypatch.setenv("BETA_ACCESS_CODE", "beta-secret-123")

        response = client.post(f"/api/v1/sessions/{session_id}/reveal")

        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "BETA_CODE_REQUIRED"

    def test_complete_missing_beta_code(
        self, client: TestClient, test_db: Session, monkeypatch
    ) -> None:
        """Complete session returns 403 when beta code is required but missing."""
        # Create session at STEP layer to allow complete
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
            current_layer=HintLayer.STEP,
            status=SessionStatus.ACTIVE,
        )
        test_db.add(session)
        test_db.commit()

        # Enable beta gate and try to complete
        monkeypatch.setenv("BETA_ACCESS_CODE", "beta-secret-123")

        response = client.post(f"/api/v1/sessions/{session_id}/complete")

        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "BETA_CODE_REQUIRED"


@pytest.mark.contract
class TestBetaGateInvalidCode:
    """Test that endpoints return 403 when beta code is wrong."""

    def test_start_session_invalid_beta_code(self, client: TestClient, monkeypatch) -> None:
        """Session start returns 403 with invalid beta code."""
        monkeypatch.setenv("BETA_ACCESS_CODE", "beta-secret-123")

        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 2x + 5 = 11"},
            headers={"X-Beta-Code": "wrong-code"},
        )

        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "BETA_CODE_INVALID"
        assert "invalid" in data["message"].lower()

    def test_respond_invalid_beta_code(
        self, client: TestClient, test_db: Session, monkeypatch
    ) -> None:
        """Responding to hints returns 403 with invalid beta code."""
        # Create session directly in DB
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
            current_layer=HintLayer.CONCEPT,
            status=SessionStatus.ACTIVE,
        )
        test_db.add(session)
        test_db.commit()

        # Enable beta gate and try with wrong code
        monkeypatch.setenv("BETA_ACCESS_CODE", "beta-secret-123")

        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "I understand we need to isolate x by moving terms"},
            headers={"X-Beta-Code": "wrong-code"},
        )

        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "BETA_CODE_INVALID"


@pytest.mark.contract
class TestBetaGateValidCode:
    """Test that endpoints work correctly with valid beta code."""

    def test_start_session_with_valid_beta_code(self, client: TestClient, monkeypatch) -> None:
        """Session start works with valid beta code."""
        monkeypatch.setenv("BETA_ACCESS_CODE", "beta-secret-123")

        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 2x + 5 = 11"},
            headers={"X-Beta-Code": "beta-secret-123"},
        )

        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data

    def test_respond_with_valid_beta_code(self, client: TestClient, monkeypatch) -> None:
        """Responding to hints works with valid beta code."""
        monkeypatch.setenv("BETA_ACCESS_CODE", "beta-secret-123")

        # First create a session with valid beta code
        start_response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 2x + 5 = 11"},
            headers={"X-Beta-Code": "beta-secret-123"},
        )
        session_id = start_response.json()["session_id"]

        # Then respond with valid beta code
        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "I understand we need to isolate x by moving terms"},
            headers={"X-Beta-Code": "beta-secret-123"},
        )

        assert response.status_code == 200

    def test_reveal_with_valid_beta_code(self, client: TestClient, monkeypatch) -> None:
        """Reveal solution works with valid beta code."""
        monkeypatch.setenv("BETA_ACCESS_CODE", "beta-secret-123")
        headers = {"X-Beta-Code": "beta-secret-123"}

        # Create session and advance to STEP layer
        start_response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 2x + 5 = 11"},
            headers=headers,
        )
        session_id = start_response.json()["session_id"]

        # Advance through layers with keyword responses
        for _ in range(2):  # CONCEPT -> STRATEGY -> STEP
            client.post(
                f"/api/v1/sessions/{session_id}/respond",
                json={"response_text": "I understand, we move terms by adding or subtracting"},
                headers=headers,
            )

        # Now try reveal
        response = client.post(f"/api/v1/sessions/{session_id}/reveal", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "final_answer" in data

    def test_complete_with_valid_beta_code(self, client: TestClient, monkeypatch) -> None:
        """Complete session works with valid beta code."""
        monkeypatch.setenv("BETA_ACCESS_CODE", "beta-secret-123")
        headers = {"X-Beta-Code": "beta-secret-123"}

        # Create session and advance to STEP layer
        start_response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 2x + 5 = 11"},
            headers=headers,
        )
        session_id = start_response.json()["session_id"]

        # Advance through layers
        for _ in range(2):  # CONCEPT -> STRATEGY -> STEP
            client.post(
                f"/api/v1/sessions/{session_id}/respond",
                json={"response_text": "I understand, we move terms by adding or subtracting"},
                headers=headers,
            )

        # Now try complete
        response = client.post(f"/api/v1/sessions/{session_id}/complete", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"


@pytest.mark.contract
class TestBetaGateDoesNotAffectPublicEndpoints:
    """Test that non-gated endpoints remain accessible regardless of beta gate."""

    def test_health_check_accessible_without_beta_code(
        self, client: TestClient, monkeypatch
    ) -> None:
        """Health check is always accessible."""
        monkeypatch.setenv("BETA_ACCESS_CODE", "beta-secret-123")

        response = client.get("/api/v1/health")

        assert response.status_code == 200

    def test_feedback_list_accessible_without_beta_code(
        self, client: TestClient, monkeypatch
    ) -> None:
        """Feedback list is accessible without beta code."""
        monkeypatch.setenv("BETA_ACCESS_CODE", "beta-secret-123")

        response = client.get("/api/v1/feedback/list")

        assert response.status_code == 200

    def test_unsubscribe_accessible_without_beta_code(
        self, client: TestClient, monkeypatch
    ) -> None:
        """Unsubscribe endpoint is accessible without beta code."""
        monkeypatch.setenv("BETA_ACCESS_CODE", "beta-secret-123")

        response = client.post(
            "/api/v1/email/unsubscribe",
            json={"email": "test@example.com", "reason": "test"},
        )

        # May return 200 or 404 depending on email existence, but not 403
        assert response.status_code != 403
