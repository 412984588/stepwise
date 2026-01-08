"""Contract tests for weekly digest script."""

import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from backend.models.session import HintSession
from backend.models.problem import Problem
from backend.models.enums import HintLayer, SessionStatus, ProblemType
from backend.scripts.send_weekly_digests import send_weekly_digests
from backend.services.email_service import EmailService


class TestWeeklyDigestScript:
    """Test the send_weekly_digests script end-to-end."""

    @pytest.mark.contract
    def test_script_runs_without_errors_when_no_sessions(
        self, test_db: Session, email_service: EmailService
    ) -> None:
        """Script should run successfully even when there are no sessions."""
        # Act
        result = send_weekly_digests(test_db, email_service, days=7, dry_run=False)

        # Assert
        assert result["total_emails"] == 0
        assert result["sent"] == 0
        assert result["failed"] == 0
        assert result["skipped"] == 0

    @pytest.mark.contract
    def test_script_finds_parent_emails_from_recent_sessions(
        self, test_db: Session, email_service: EmailService
    ) -> None:
        """Script should find all unique parent emails from recent sessions."""
        # Arrange: Create sessions with parent emails
        problem = Problem(
            raw_text="2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        # Session 1: parent1@example.com (3 days ago)
        session1 = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.STEP,
            status=SessionStatus.COMPLETED,
            parent_email="parent1@example.com",
            started_at=datetime.now(timezone.utc) - timedelta(days=3),
        )
        test_db.add(session1)

        # Session 2: parent2@example.com (5 days ago)
        session2 = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.STEP,
            status=SessionStatus.COMPLETED,
            parent_email="parent2@example.com",
            started_at=datetime.now(timezone.utc) - timedelta(days=5),
        )
        test_db.add(session2)

        # Session 3: parent1@example.com again (2 days ago)
        session3 = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.CONCEPT,
            status=SessionStatus.ACTIVE,
            parent_email="parent1@example.com",
            started_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        test_db.add(session3)

        test_db.commit()

        # Act
        result = send_weekly_digests(test_db, email_service, days=7, dry_run=False)

        # Assert: Should find 2 unique emails
        assert result["total_emails"] == 2
        assert result["sent"] == 2
        assert result["failed"] == 0

    @pytest.mark.contract
    def test_script_respects_date_range(
        self, test_db: Session, email_service: EmailService
    ) -> None:
        """Script should only include sessions within the specified date range."""
        # Arrange
        problem = Problem(
            raw_text="2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        # Recent session (3 days ago)
        recent_session = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.STEP,
            status=SessionStatus.COMPLETED,
            parent_email="recent@example.com",
            started_at=datetime.now(timezone.utc) - timedelta(days=3),
        )
        test_db.add(recent_session)

        # Old session (10 days ago)
        old_session = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.STEP,
            status=SessionStatus.COMPLETED,
            parent_email="old@example.com",
            started_at=datetime.now(timezone.utc) - timedelta(days=10),
        )
        test_db.add(old_session)

        test_db.commit()

        # Act: Run with 7-day lookback
        result = send_weekly_digests(test_db, email_service, days=7, dry_run=False)

        # Assert: Should only find recent email
        assert result["total_emails"] == 1
        assert result["sent"] == 1

    @pytest.mark.contract
    def test_script_dry_run_does_not_send_emails(
        self, test_db: Session, email_service: EmailService
    ) -> None:
        """Dry run mode should preview without actually sending emails."""
        # Arrange
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
            parent_email="parent@example.com",
            started_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        test_db.add(session)
        test_db.commit()

        # Act: Run in dry-run mode
        result = send_weekly_digests(test_db, email_service, days=7, dry_run=True)

        # Assert: Should find emails and count them as "sent" (dry-run counts what would be sent)
        assert result["total_emails"] == 1
        assert result["sent"] == 1  # Dry run counts what would be sent
        assert result["skipped"] == 0

    @pytest.mark.contract
    def test_script_continues_on_email_failure(
        self, test_db: Session, email_service: EmailService, monkeypatch
    ) -> None:
        """Script should continue processing if one email fails."""
        # Arrange
        problem = Problem(
            raw_text="2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        # Create two sessions with different emails
        session1 = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.STEP,
            status=SessionStatus.COMPLETED,
            parent_email="parent1@example.com",
            started_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        test_db.add(session1)

        session2 = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.STEP,
            status=SessionStatus.COMPLETED,
            parent_email="parent2@example.com",
            started_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        test_db.add(session2)
        test_db.commit()

        # Mock email service to fail on first email
        call_count = 0

        def mock_send_weekly_digest(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return False  # First email fails
            return True  # Second email succeeds

        monkeypatch.setattr(email_service, "send_weekly_digest", mock_send_weekly_digest)

        # Act
        result = send_weekly_digests(test_db, email_service, days=7, dry_run=False)

        # Assert: Should process both emails
        assert result["total_emails"] == 2
        assert result["sent"] == 1  # One succeeded
        assert result["failed"] == 1  # One failed

    @pytest.mark.contract
    def test_script_skips_sessions_without_email(
        self, test_db: Session, email_service: EmailService
    ) -> None:
        """Script should only process sessions that have parent emails."""
        # Arrange
        problem = Problem(
            raw_text="2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        # Session with email
        session_with_email = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.STEP,
            status=SessionStatus.COMPLETED,
            parent_email="parent@example.com",
            started_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        test_db.add(session_with_email)

        # Session without email
        session_without_email = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.STEP,
            status=SessionStatus.COMPLETED,
            parent_email=None,
            started_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        test_db.add(session_without_email)

        test_db.commit()

        # Act
        result = send_weekly_digests(test_db, email_service, days=7, dry_run=False)

        # Assert: Should only find the one with email
        assert result["total_emails"] == 1
        assert result["sent"] == 1

    @pytest.mark.contract
    def test_script_aggregates_multiple_sessions_per_email(
        self, test_db: Session, email_service: EmailService
    ) -> None:
        """Script should aggregate all sessions for the same parent email."""
        # Arrange
        problem = Problem(
            raw_text="2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        # Create 3 sessions for the same parent
        for i in range(3):
            session = HintSession(
                problem_id=problem.id,
                current_layer=HintLayer.STEP,
                status=SessionStatus.COMPLETED,
                parent_email="parent@example.com",
                started_at=datetime.now(timezone.utc) - timedelta(days=i + 1),
            )
            test_db.add(session)

        test_db.commit()

        # Act
        result = send_weekly_digests(test_db, email_service, days=7, dry_run=False)

        # Assert: Should send only 1 email (aggregated)
        assert result["total_emails"] == 1
        assert result["sent"] == 1

    @pytest.mark.contract
    def test_script_with_custom_days_parameter(
        self, test_db: Session, email_service: EmailService
    ) -> None:
        """Script should respect custom days parameter."""
        # Arrange
        problem = Problem(
            raw_text="2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        # Session 2 days ago
        session = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.STEP,
            status=SessionStatus.COMPLETED,
            parent_email="parent@example.com",
            started_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        test_db.add(session)
        test_db.commit()

        # Act: Run with 1-day lookback (should not find the 2-day-old session)
        result = send_weekly_digests(test_db, email_service, days=1, dry_run=False)

        # Assert: Should find no emails
        assert result["total_emails"] == 0
        assert result["sent"] == 0
