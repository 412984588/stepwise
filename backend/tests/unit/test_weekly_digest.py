import pytest
from datetime import datetime, timedelta, timezone

from backend.services.weekly_digest import WeeklyDigestGenerator
from backend.models.session import HintSession
from backend.models.problem import Problem
from backend.models.enums import HintLayer, SessionStatus, ProblemType


@pytest.mark.unit
class TestWeeklyDigestGenerator:
    def test_generate_digest_returns_none_for_no_sessions(self, test_db):
        generator = WeeklyDigestGenerator()
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        result = generator.generate_weekly_digest(
            test_db, "nonexistent@example.com", start_date, end_date
        )

        assert result is None

    def test_generate_digest_with_single_completed_session(self, test_db):
        generator = WeeklyDigestGenerator()
        email = "parent@example.com"

        problem = Problem(
            raw_text="Test problem",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            difficulty="EASY",
        )
        test_db.add(problem)
        test_db.flush()

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)
        session_time = start_date + timedelta(days=1)

        session = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            status=SessionStatus.COMPLETED,
            parent_email=email,
            started_at=session_time,
            completed_at=session_time + timedelta(minutes=15),
            confusion_count=1,
            used_full_solution=False,
        )
        test_db.add(session)
        test_db.commit()

        result = generator.generate_weekly_digest(test_db, email, start_date, end_date)

        assert result is not None
        assert result["email"] == email
        assert result["total_sessions"] == 1
        assert result["completed_sessions"] == 1
        assert result["total_time_minutes"] == 15
        assert result["reveal_usage_count"] == 0
        assert result["highest_layer_reached"] == "step"

    def test_calculate_performance_level_excellent(self, test_db):
        generator = WeeklyDigestGenerator()
        email = "parent@example.com"

        problem = Problem(
            raw_text="Test problem",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            difficulty="EASY",
        )
        test_db.add(problem)
        test_db.flush()

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        for i in range(10):
            session = HintSession(
                problem_id=problem.id,
                current_layer=HintLayer.COMPLETED,
                status=SessionStatus.COMPLETED,
                parent_email=email,
                started_at=start_date + timedelta(hours=i),
                completed_at=start_date + timedelta(hours=i, minutes=10),
                confusion_count=0,
                used_full_solution=False,
            )
            test_db.add(session)

        test_db.commit()

        result = generator.generate_weekly_digest(test_db, email, start_date, end_date)

        assert result["performance_level"] == "Excellent"

    def test_calculate_performance_level_needs_practice(self, test_db):
        generator = WeeklyDigestGenerator()
        email = "parent@example.com"

        problem = Problem(
            raw_text="Test problem",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            difficulty="EASY",
        )
        test_db.add(problem)
        test_db.flush()

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        for i in range(10):
            session = HintSession(
                problem_id=problem.id,
                current_layer=HintLayer.CONCEPT,
                status=SessionStatus.ACTIVE,
                parent_email=email,
                started_at=start_date + timedelta(hours=i),
                completed_at=None,
                confusion_count=3,
                used_full_solution=True,
            )
            test_db.add(session)

        test_db.commit()

        result = generator.generate_weekly_digest(test_db, email, start_date, end_date)

        assert result["performance_level"] == "Needs Practice"

    def test_generate_recommendations_for_low_completion(self, test_db):
        generator = WeeklyDigestGenerator()
        email = "parent@example.com"

        problem = Problem(
            raw_text="Test problem",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            difficulty="EASY",
        )
        test_db.add(problem)
        test_db.flush()

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        for i in range(10):
            session = HintSession(
                problem_id=problem.id,
                current_layer=HintLayer.STRATEGY,
                status=SessionStatus.ACTIVE,
                parent_email=email,
                started_at=start_date + timedelta(hours=i),
                completed_at=None,
                confusion_count=1,
                used_full_solution=False,
            )
            test_db.add(session)

        test_db.commit()

        result = generator.generate_weekly_digest(test_db, email, start_date, end_date)

        recommendations = result["recommendations"]
        assert len(recommendations) > 0
        assert any("independently" in rec.lower() for rec in recommendations)

    def test_generate_recommendations_for_high_reveal_usage(self, test_db):
        generator = WeeklyDigestGenerator()
        email = "parent@example.com"

        problem = Problem(
            raw_text="Test problem",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            difficulty="EASY",
        )
        test_db.add(problem)
        test_db.flush()

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        for i in range(10):
            session = HintSession(
                problem_id=problem.id,
                current_layer=HintLayer.COMPLETED,
                status=SessionStatus.COMPLETED,
                parent_email=email,
                started_at=start_date + timedelta(hours=i),
                completed_at=start_date + timedelta(hours=i, minutes=10),
                confusion_count=0,
                used_full_solution=True,
            )
            test_db.add(session)

        test_db.commit()

        result = generator.generate_weekly_digest(test_db, email, start_date, end_date)

        recommendations = result["recommendations"]
        assert len(recommendations) > 0
        assert any(
            "hint layer" in rec.lower() or "revealing" in rec.lower() for rec in recommendations
        )

    def test_identify_most_challenging_topic(self, test_db):
        generator = WeeklyDigestGenerator()
        email = "parent@example.com"

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        for problem_type in [ProblemType.QUADRATIC_EQUATION] * 5 + [
            ProblemType.LINEAR_EQUATION_1VAR
        ]:
            problem = Problem(raw_text="Test problem", problem_type=problem_type, difficulty="EASY")
            test_db.add(problem)
            test_db.flush()

            session = HintSession(
                problem_id=problem.id,
                current_layer=HintLayer.CONCEPT,
                status=SessionStatus.ACTIVE,
                parent_email=email,
                started_at=start_date + timedelta(hours=1),
                completed_at=None,
                confusion_count=3,
                used_full_solution=False,
            )
            test_db.add(session)

        test_db.commit()

        result = generator.generate_weekly_digest(test_db, email, start_date, end_date)

        assert "Quadratic" in result["most_challenging_topic"]

    def test_date_range_filtering(self, test_db):
        generator = WeeklyDigestGenerator()
        email = "parent@example.com"

        problem = Problem(
            raw_text="Test problem",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            difficulty="EASY",
        )
        test_db.add(problem)
        test_db.flush()

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)
        old_date = start_date - timedelta(days=10)

        session_in_range = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            status=SessionStatus.COMPLETED,
            parent_email=email,
            started_at=start_date + timedelta(days=1),
            completed_at=start_date + timedelta(days=1, minutes=10),
            confusion_count=0,
            used_full_solution=False,
        )
        test_db.add(session_in_range)

        session_out_of_range = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            status=SessionStatus.COMPLETED,
            parent_email=email,
            started_at=old_date,
            completed_at=old_date + timedelta(minutes=10),
            confusion_count=0,
            used_full_solution=False,
        )
        test_db.add(session_out_of_range)

        test_db.commit()

        result = generator.generate_weekly_digest(test_db, email, start_date, end_date)

        assert result["total_sessions"] == 1
