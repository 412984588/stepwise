#!/usr/bin/env python3
"""
Seed demo data for local QA testing.

Creates sample users, problems, hint sessions, and feedback for manual testing.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.database.engine import SessionLocal
from backend.models.problem import Problem
from backend.models.session import HintSession
from backend.models.response import StudentResponse
from backend.models.hint_content import HintContent
from backend.models.feedback import FeedbackItem
from backend.models.enums import HintLayer, UnderstandingLevel, ProblemType


def seed_demo_data(db: Session) -> None:
    """Seed demo data for local QA."""

    print("🌱 Seeding demo data...")

    # Create demo problems
    problems = [
        Problem(
            raw_text="Solve for x: 2x + 5 = 11",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            grade_level=7,
        ),
        Problem(
            raw_text="Factor: x² - 5x + 6",
            problem_type=ProblemType.QUADRATIC_EQUATION,
            grade_level=8,
        ),
        Problem(
            raw_text="Find the area of a circle with radius 5cm",
            problem_type=ProblemType.GEOMETRY_BASIC,
            grade_level=6,
        ),
        Problem(
            raw_text="Simplify: 3(x + 2) - 2(x - 1)",
            problem_type=ProblemType.LINEAR_EQUATION_1VAR,
            grade_level=7,
        ),
        Problem(
            raw_text="What is 15% of 80?",
            problem_type=ProblemType.ARITHMETIC,
            grade_level=6,
        ),
    ]

    for problem in problems:
        db.add(problem)

    db.commit()
    print(f"✅ Created {len(problems)} demo problems")

    # Create demo hint sessions
    sessions = []
    parent_emails = [
        "parent1@example.com",
        "parent2@example.com",
        None,  # Anonymous session
    ]

    for i, problem in enumerate(problems[:3]):
        # Create completed session
        session = HintSession(
            problem_id=problem.id,
            current_layer=HintLayer.COMPLETED,
            confusion_count=0,
            parent_email=parent_emails[i % len(parent_emails)],
        )
        db.add(session)
        db.flush()  # Get the ID

        # Add hint contents
        hint_concept = HintContent(
            session_id=session.id,
            layer=HintLayer.CONCEPT,
            content=f"This is a {problem.problem_type.value} problem. Think about what mathematical concept applies here.",
            is_downgrade=False,
        )
        db.add(hint_concept)

        hint_strategy = HintContent(
            session_id=session.id,
            layer=HintLayer.STRATEGY,
            content="Let's break this down step by step. What should we do first?",
            is_downgrade=False,
        )
        db.add(hint_strategy)

        # Add student responses
        response1 = StudentResponse(
            session_id=session.id,
            layer=HintLayer.CONCEPT,
            char_count=42,
            understanding_level=UnderstandingLevel.UNDERSTOOD,
            keywords_matched=["equation", "solving"],
        )
        db.add(response1)

        response2 = StudentResponse(
            session_id=session.id,
            layer=HintLayer.STRATEGY,
            char_count=35,
            understanding_level=UnderstandingLevel.UNDERSTOOD,
            keywords_matched=["isolate", "variable"],
        )
        db.add(response2)

        sessions.append(session)

    db.commit()
    print(f"✅ Created {len(sessions)} demo hint sessions with responses")

    # Create demo feedback
    feedback_items = [
        FeedbackItem(
            locale="en-US",
            grade_level="grade_7",
            pmf_answer="very_disappointed",
            would_pay="yes_definitely",
            what_worked="The layered hints really helped my daughter understand algebra step by step.",
            what_confused="Nothing major, just wish there were more geometry problems.",
            email="parent1@example.com",
        ),
        FeedbackItem(
            locale="en-US",
            grade_level="grade_8",
            pmf_answer="very_disappointed",
            would_pay="yes_probably",
            what_worked="Love the Socratic approach - teaches problem-solving, not just answers.",
            what_confused="Would like more practice problems at each level.",
            email="parent2@example.com",
        ),
        FeedbackItem(
            locale="en-US",
            grade_level="grade_6",
            pmf_answer="somewhat_disappointed",
            would_pay="not_sure",
            what_worked="The concept hints are great for building understanding.",
            what_confused=None,
            email=None,
        ),
    ]

    for feedback in feedback_items:
        db.add(feedback)

    db.commit()
    print(f"✅ Created {len(feedback_items)} demo feedback items")

    print("\n🎉 Demo data seeding complete!")
    print("\n📊 Summary:")
    print(f"  - Problems: {len(problems)}")
    print(f"  - Hint Sessions: {len(sessions)}")
    print(f"  - Feedback Items: {len(feedback_items)}")
    print(f"\n💡 You can now test the app with realistic data!")


def main() -> None:
    """Main entry point."""
    print("=" * 60)
    print("StepWise Demo Data Seeder")
    print("=" * 60)
    print()

    # Get database session
    db = SessionLocal()

    try:
        seed_demo_data(db)
    except Exception as e:
        print(f"\n❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
