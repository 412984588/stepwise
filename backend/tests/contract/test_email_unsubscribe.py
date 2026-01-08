"""Contract tests for email unsubscribe endpoint."""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models.session import HintSession
from backend.models.problem import Problem
from backend.models.enums import HintLayer, SessionStatus, ProblemType
from backend.services.email_preference_service import EmailPreferenceService
from backend.scripts.send_weekly_digests import send_weekly_digests
from backend.services.email_service import EmailService


class TestUnsubscribeEndpoint:
    """Tests for GET /email/unsubscribe/{token} endpoint."""

    @pytest.mark.contract
    def test_unsubscribe_with_valid_token_returns_200(
        self, client: TestClient, test_db: Session
    ) -> None:
        """Should return 200 with success HTML for valid token."""
        email = "parent@example.com"
        preference = EmailPreferenceService.get_or_create_preference(test_db, email)
        token = preference.unsubscribe_token

        response = client.get(f"/api/v1/email/unsubscribe/{token}")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "You have been unsubscribed" in response.text

    @pytest.mark.contract
    def test_unsubscribe_marks_preference_as_disabled(
        self, client: TestClient, test_db: Session
    ) -> None:
        """Should mark weekly_digest_enabled as False."""
        email = "parent@example.com"
        preference = EmailPreferenceService.get_or_create_preference(test_db, email)
        token = preference.unsubscribe_token

        # Initially enabled
        assert preference.weekly_digest_enabled is True

        # Unsubscribe
        response = client.get(f"/api/v1/email/unsubscribe/{token}")

        assert response.status_code == 200

        # Check it's disabled
        test_db.refresh(preference)
        assert preference.weekly_digest_enabled is False

    @pytest.mark.contract
    def test_unsubscribe_with_invalid_token_returns_200_error_page(
        self, client: TestClient, test_db: Session
    ) -> None:
        """Should return 200 with error HTML for invalid token."""
        invalid_token = "00000000-0000-0000-0000-000000000000"

        response = client.get(f"/api/v1/email/unsubscribe/{invalid_token}")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Invalid or Expired Link" in response.text

    @pytest.mark.contract
    def test_unsubscribe_with_malformed_token_returns_400(
        self, client: TestClient, test_db: Session
    ) -> None:
        """Should return 400 for malformed token."""
        malformed_token = "not-a-valid-uuid"

        response = client.get(f"/api/v1/email/unsubscribe/{malformed_token}")

        assert response.status_code == 400
        data = response.json()
        # The custom exception handler flattens HTTPException.detail
        assert "Invalid unsubscribe token format" in data.get(
            "message", ""
        ) or "Invalid unsubscribe token format" in str(data)

    @pytest.mark.contract
    def test_unsubscribe_is_idempotent(self, client: TestClient, test_db: Session) -> None:
        """Should work correctly when called multiple times."""
        email = "parent@example.com"
        preference = EmailPreferenceService.get_or_create_preference(test_db, email)
        token = preference.unsubscribe_token

        # Unsubscribe first time
        response1 = client.get(f"/api/v1/email/unsubscribe/{token}")
        assert response1.status_code == 200

        # Unsubscribe second time
        response2 = client.get(f"/api/v1/email/unsubscribe/{token}")
        assert response2.status_code == 200

        # Still disabled
        test_db.refresh(preference)
        assert preference.weekly_digest_enabled is False

    @pytest.mark.contract
    def test_unsubscribe_html_contains_note_about_session_emails(
        self, client: TestClient, test_db: Session
    ) -> None:
        """Success page should clarify that session emails are not affected."""
        email = "parent@example.com"
        preference = EmailPreferenceService.get_or_create_preference(test_db, email)
        token = preference.unsubscribe_token

        response = client.get(f"/api/v1/email/unsubscribe/{token}")

        assert response.status_code == 200
        # Should mention that session completion emails are still sent
        assert "session" in response.text.lower() or "child completes" in response.text.lower()


class TestFullUnsubscribeFlow:
    """Test complete unsubscribe workflow."""

    @pytest.mark.contract
    def test_unsubscribe_prevents_future_weekly_digests(
        self, client: TestClient, test_db: Session, email_service: EmailService
    ) -> None:
        """After unsubscribing, should not receive future weekly digests."""
        email = "parent@example.com"

        # Create a session with this email
        problem = Problem(
            raw_text="2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        session = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.STEP,
            status=SessionStatus.COMPLETED,
            parent_email=email,
            started_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        test_db.add(session)
        test_db.commit()

        # Get unsubscribe token
        preference = EmailPreferenceService.get_or_create_preference(test_db, email)
        token = preference.unsubscribe_token

        # Verify weekly digest can be sent initially
        result1 = send_weekly_digests(test_db, email_service, days=7, dry_run=False)
        assert result1["sent"] == 1

        # Unsubscribe
        response = client.get(f"/api/v1/email/unsubscribe/{token}")
        assert response.status_code == 200

        # Try to send weekly digest again - should be skipped
        result2 = send_weekly_digests(test_db, email_service, days=7, dry_run=False)
        assert result2["sent"] == 0
        assert result2["skipped"] == 1

    @pytest.mark.contract
    def test_weekly_digest_email_contains_unsubscribe_link(
        self, client: TestClient, test_db: Session, email_service: EmailService
    ) -> None:
        """Weekly digest email should contain unsubscribe link."""
        email = "parent@example.com"

        # Create email preference to get token
        preference = EmailPreferenceService.get_or_create_preference(test_db, email)
        token = preference.unsubscribe_token

        # Create digest data
        digest_data = {
            "total_sessions": 5,
            "completed_sessions": 4,
            "highest_layer_reached": "step",
            "total_time_minutes": 45,
            "reveal_usage_count": 1,
            "most_challenging_topic": "Linear equations",
            "performance_level": "Good",
            "recommendations": ["Keep practicing!", "Try harder problems"],
        }

        # Compose email HTML
        html = email_service._compose_weekly_digest_html(digest_data, token)

        # Should contain unsubscribe link
        assert "unsubscribe" in html.lower()
        assert token in html
        assert "/email/unsubscribe/" in html

    @pytest.mark.contract
    def test_weekly_digest_without_token_has_no_unsubscribe_link(
        self, client: TestClient, test_db: Session, email_service: EmailService
    ) -> None:
        """Weekly digest without token should not have unsubscribe link."""
        digest_data = {
            "total_sessions": 5,
            "completed_sessions": 4,
            "highest_layer_reached": "step",
            "total_time_minutes": 45,
            "reveal_usage_count": 1,
            "most_challenging_topic": "Linear equations",
            "performance_level": "Good",
            "recommendations": ["Keep practicing!"],
        }

        # Compose email HTML without token
        html = email_service._compose_weekly_digest_html(digest_data, None)

        # Should not contain unsubscribe link
        assert "unsubscribe" not in html.lower() or "/email/unsubscribe/" not in html
