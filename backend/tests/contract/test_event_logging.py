"""Contract tests for event logging functionality."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import EventLog


@pytest.mark.contract
class TestEventLogging:
    """Test event logging during session lifecycle."""

    def test_session_start_logs_events(self, client: TestClient, test_db: Session) -> None:
        """Test that starting a session logs session_started and concept_hint_given events."""
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 2x + 5 = 11", "locale": "en-US", "grade_level": 7},
        )

        assert response.status_code == 201
        data = response.json()
        session_id = data["session_id"]

        # Check that events were logged
        events = test_db.query(EventLog).filter(EventLog.session_id == session_id).all()

        assert len(events) >= 2
        event_types = [e.event_type for e in events]
        assert "session_started" in event_types
        assert "concept_hint_given" in event_types

    def test_layer_advancement_logs_events(self, client: TestClient, test_db: Session) -> None:
        """Test that advancing layers logs appropriate events."""
        # Start session
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 3x + 7 = 16", "locale": "en-US", "grade_level": 7},
        )
        session_id = response.json()["session_id"]

        # Respond with understanding to advance
        response = client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "I understand the concept of linear equations and variables"},
        )

        assert response.status_code == 200
        data = response.json()

        # If advanced to strategy layer, check for events
        if data["current_layer"] == "STRATEGY":
            events = test_db.query(EventLog).filter(EventLog.session_id == session_id).all()
            event_types = [e.event_type for e in events]
            assert "reached_strategy_layer" in event_types
            assert "strategy_hint_given" in event_types

    def test_reveal_solution_logs_event(self, client: TestClient, test_db: Session) -> None:
        """Test that revealing solution logs reveal_used event."""
        # Start session
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 2x + 5 = 11", "locale": "en-US", "grade_level": 7},
        )
        session_id = response.json()["session_id"]

        # Advance to step layer by responding with understanding
        # Advance from CONCEPT to STRATEGY
        client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "I understand this is a linear equation with one variable"},
        )

        # Advance from STRATEGY to STEP
        client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "I will isolate x by using inverse operations on both sides"},
        )

        # Now at STEP layer, reveal is allowed
        response = client.post(f"/api/v1/sessions/{session_id}/reveal")

        assert response.status_code == 200

        # Check for reveal event
        events = test_db.query(EventLog).filter(EventLog.session_id == session_id).all()
        event_types = [e.event_type for e in events]
        assert "reveal_used" in event_types

    def test_complete_session_logs_event(self, client: TestClient, test_db: Session) -> None:
        """Test that completing session logs session_completed event."""
        # Start session
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve 5x = 20", "locale": "en-US", "grade_level": 6},
        )
        session_id = response.json()["session_id"]

        # Advance to step layer
        client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "I understand this is a simple equation"},
        )
        client.post(
            f"/api/v1/sessions/{session_id}/respond",
            json={"response_text": "I will divide both sides by 5"},
        )

        # Complete session
        response = client.post(f"/api/v1/sessions/{session_id}/complete")

        assert response.status_code == 200

        # Check for completion event
        events = test_db.query(EventLog).filter(EventLog.session_id == session_id).all()
        event_types = [e.event_type for e in events]
        assert "session_completed" in event_types

    def test_custom_event_logging_endpoint(self, client: TestClient, test_db: Session) -> None:
        """Test that custom event logging endpoint works."""
        # Start session
        response = client.post(
            "/api/v1/sessions/start",
            json={"problem_text": "Solve x + 3 = 7", "locale": "en-US", "grade_level": 5},
        )
        session_id = response.json()["session_id"]

        # Log custom event
        response = client.post(
            f"/api/v1/sessions/{session_id}/events",
            json={"event_type": "ui_interaction", "details": {"action": "clicked_hint"}},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["event_type"] == "ui_interaction"

        # Verify event was logged
        events = test_db.query(EventLog).filter(EventLog.session_id == session_id).all()
        event_types = [e.event_type for e in events]
        assert "ui_interaction" in event_types

    def test_custom_event_invalid_session(self, client: TestClient) -> None:
        """Test that logging event to non-existent session returns 404."""
        response = client.post(
            "/api/v1/sessions/nonexistent_session/events",
            json={"event_type": "test_event"},
        )

        assert response.status_code == 404
        assert response.json()["error"] == "SESSION_NOT_FOUND"
