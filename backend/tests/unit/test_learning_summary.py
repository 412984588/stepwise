"""Unit tests for learning summary generation."""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from backend.models import (
    HintSession,
    Problem,
    EventLog,
    HintLayer,
    SessionStatus,
    ProblemType,
)
from backend.services.learning_summary import LearningSummaryGenerator


@pytest.mark.unit
class TestLearningSummaryExcellent:
    """Test summary generation for excellent performance."""

    def test_completed_no_confusion_excellent(self, test_db: Session) -> None:
        """Test that completed session with no confusion gets Excellent rating."""
        problem = Problem(
            raw_text="Solve 2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        session = HintSession(
            id="test_excellent",
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            status=SessionStatus.COMPLETED,
            confusion_count=0,
            used_full_solution=False,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            completed_at=datetime.now(timezone.utc),
        )
        test_db.add(session)

        event1 = EventLog(
            session_id="test_excellent",
            event_type="session_started",
        )
        event2 = EventLog(
            session_id="test_excellent",
            event_type="reached_strategy_layer",
        )
        event3 = EventLog(
            session_id="test_excellent",
            event_type="reached_step_layer",
        )
        test_db.add(event1)
        test_db.add(event2)
        test_db.add(event3)
        test_db.commit()

        generator = LearningSummaryGenerator()
        summary = generator.generate_session_summary(test_db, "test_excellent")

        assert summary["performance_level"] == "Excellent"
        assert "Linear Equations" in summary["headline"]
        assert len(summary["insights"]) > 0
        assert "independently" in summary["insights"][0].lower()


@pytest.mark.unit
class TestLearningSummaryGood:
    """Test summary generation for good performance."""

    def test_completed_low_confusion_good(self, test_db: Session) -> None:
        """Test that completed session with low confusion gets Good rating."""
        problem = Problem(
            raw_text="Find area of triangle",
            problem_type=ProblemType.GEOMETRY_BASIC,
        )
        test_db.add(problem)
        test_db.flush()

        session = HintSession(
            id="test_good",
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            status=SessionStatus.COMPLETED,
            confusion_count=2,
            used_full_solution=False,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=8),
            completed_at=datetime.now(timezone.utc),
        )
        test_db.add(session)
        test_db.commit()

        generator = LearningSummaryGenerator()
        summary = generator.generate_session_summary(test_db, "test_good")

        assert summary["performance_level"] == "Good"
        assert "Geometry" in summary["headline"]


@pytest.mark.unit
class TestLearningSummaryNeedsPractice:
    """Test summary generation for needs practice."""

    def test_used_reveal_needs_practice(self, test_db: Session) -> None:
        """Test that using reveal solution triggers Needs Practice."""
        problem = Problem(
            raw_text="Solve x² - 4 = 0",
            problem_type=ProblemType.QUADRATIC_EQUATION,
        )
        test_db.add(problem)
        test_db.flush()

        session = HintSession(
            id="test_needs",
            problem_id=problem.id,
            current_layer=HintLayer.STEP,
            status=SessionStatus.REVEALED,
            confusion_count=3,
            used_full_solution=True,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=15),
        )
        test_db.add(session)
        test_db.commit()

        generator = LearningSummaryGenerator()
        summary = generator.generate_session_summary(test_db, "test_needs")

        assert summary["performance_level"] == "Needs Practice"
        assert "reveal" in summary["insights"][1].lower()


@pytest.mark.unit
class TestConfusionAnalysis:
    """Test confusion analysis logic."""

    def test_confusion_at_strategy_layer(self, test_db: Session) -> None:
        """Test confusion analysis identifies strategy layer issues."""
        problem = Problem(
            raw_text="Solve system of equations",
            problem_type=ProblemType.LINEAR_EQUATION_2VAR,
        )
        test_db.add(problem)
        test_db.flush()

        session = HintSession(
            id="test_confusion",
            problem_id=problem.id,
            current_layer=HintLayer.STRATEGY,
            status=SessionStatus.ACTIVE,
            confusion_count=2,
        )
        test_db.add(session)

        for _ in range(3):
            event = EventLog(
                session_id="test_confusion",
                event_type="strategy_hint_given",
            )
            test_db.add(event)
        test_db.commit()

        generator = LearningSummaryGenerator()
        summary = generator.generate_session_summary(test_db, "test_confusion")

        assert "strategy" in summary["insights"][1].lower()


@pytest.mark.unit
class TestTimePacing:
    """Test time pacing calculation."""

    def test_fast_pacing(self, test_db: Session) -> None:
        """Test fast pacing detection."""
        problem = Problem(
            raw_text="5 + 10",
            problem_type=ProblemType.ARITHMETIC,
        )
        test_db.add(problem)
        test_db.flush()

        session = HintSession(
            id="test_fast",
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            status=SessionStatus.COMPLETED,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=2),
            completed_at=datetime.now(timezone.utc),
        )
        test_db.add(session)
        test_db.commit()

        generator = LearningSummaryGenerator()
        summary = generator.generate_session_summary(test_db, "test_fast")

        assert any("quick" in insight.lower() for insight in summary["insights"])

    def test_slow_pacing(self, test_db: Session) -> None:
        """Test slow pacing detection."""
        problem = Problem(
            raw_text="Complex problem",
            problem_type=ProblemType.QUADRATIC_EQUATION,
        )
        test_db.add(problem)
        test_db.flush()

        session = HintSession(
            id="test_slow",
            problem_id=problem.id,
            current_layer=HintLayer.STEP,
            status=SessionStatus.ACTIVE,
            started_at=datetime.now(timezone.utc) - timedelta(minutes=12),
        )
        test_db.add(session)
        test_db.commit()

        generator = LearningSummaryGenerator()
        summary = generator.generate_session_summary(test_db, "test_slow")

        assert any("time" in insight.lower() for insight in summary["insights"])


@pytest.mark.unit
class TestRecommendations:
    """Test recommendation generation."""

    def test_excellent_gets_challenge_recommendation(self, test_db: Session) -> None:
        """Test excellent performance gets challenging recommendation."""
        problem = Problem(
            raw_text="Simple equation",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
        )
        test_db.add(problem)
        test_db.flush()

        session = HintSession(
            id="test_rec",
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            status=SessionStatus.COMPLETED,
            confusion_count=0,
        )
        test_db.add(session)
        test_db.commit()

        generator = LearningSummaryGenerator()
        summary = generator.generate_session_summary(test_db, "test_rec")

        assert "challenging" in summary["recommendation"].lower()


@pytest.mark.unit
class TestSessionNotFound:
    """Test error handling."""

    def test_nonexistent_session_raises_error(self, test_db: Session) -> None:
        """Test that nonexistent session raises ValueError."""
        generator = LearningSummaryGenerator()

        with pytest.raises(ValueError, match="Session .* not found"):
            generator.generate_session_summary(test_db, "nonexistent")
