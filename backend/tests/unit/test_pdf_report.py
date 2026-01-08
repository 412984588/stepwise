"""Unit tests for PDF report generation."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import HintSession, Problem, EventLog, HintLayer, SessionStatus, ProblemType
from backend.utils.validation import generate_session_id


@pytest.mark.unit
class TestPDFReportGeneration:
    """Test PDF report generation endpoint."""

    def test_pdf_report_returns_correct_content_type(
        self, client: TestClient, test_db: Session
    ) -> None:
        """Test that PDF endpoint returns application/pdf content type."""
        # Create a test session
        session_id = generate_session_id()
        problem = Problem(
            raw_text="Solve 2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        access_token = HintSession.generate_access_token()
        session = HintSession(
            id=session_id,
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            status=SessionStatus.COMPLETED,
            session_access_token=access_token,
        )
        test_db.add(session)

        # Add some events
        event1 = EventLog(
            session_id=session_id,
            event_type="session_started",
            details={"problem_type": "linear_equation_1var"},
        )
        event2 = EventLog(
            session_id=session_id,
            event_type="concept_hint_given",
            details={"sequence": 1},
        )
        test_db.add(event1)
        test_db.add(event2)
        test_db.commit()

        # Request PDF with session access token
        response = client.get(
            f"/api/v1/reports/session/{session_id}/pdf",
            headers={"X-Session-Access-Token": access_token},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert f"stepwise_session_{session_id}.pdf" in response.headers["content-disposition"]

    def test_pdf_report_contains_content(self, client: TestClient, test_db: Session) -> None:
        """Test that PDF contains actual content (not empty)."""
        # Create a test session
        session_id = generate_session_id()
        problem = Problem(
            raw_text="Calculate 15 + 27",
            problem_type=ProblemType.ARITHMETIC,
        )
        test_db.add(problem)
        test_db.flush()

        access_token = HintSession.generate_access_token()
        session = HintSession(
            id=session_id,
            problem_id=problem.id,
            current_layer=HintLayer.STEP,
            status=SessionStatus.ACTIVE,
            session_access_token=access_token,
        )
        test_db.add(session)
        test_db.commit()

        # Request PDF with session access token
        response = client.get(
            f"/api/v1/reports/session/{session_id}/pdf",
            headers={"X-Session-Access-Token": access_token},
        )

        assert response.status_code == 200
        # PDF should have content (at least 1KB for a minimal PDF)
        assert len(response.content) > 1000
        # PDF files start with %PDF
        assert response.content[:4] == b"%PDF"

    def test_pdf_report_not_found_for_invalid_session(self, client: TestClient) -> None:
        """Test that requesting PDF for non-existent session returns 404."""
        # Provide a token so we get past token validation to session lookup
        fake_token = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            "/api/v1/reports/session/00000000-0000-0000-0000-000000000000/pdf",
            headers={"X-Session-Access-Token": fake_token},
        )

        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "SESSION_NOT_FOUND"
