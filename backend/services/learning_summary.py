"""Learning summary generation service for session analysis."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from backend.models import HintSession, Problem, EventLog, HintLayer, SessionStatus


@dataclass
class SessionSummary:
    """Structured session learning summary."""

    headline: str
    performance_level: str
    insights: list[str]
    recommendation: str


class LearningSummaryGenerator:
    """Generates parent-friendly learning summaries from session data."""

    def generate_session_summary(self, db: Session, session_id: str) -> dict[str, Any]:
        """Generate a comprehensive learning summary for a session.

        Args:
            db: Database session
            session_id: Session ID to summarize

        Returns:
            Dictionary with headline, performance_level, insights, and recommendation
        """
        session = db.query(HintSession).filter(HintSession.id == session_id).first()
        if not session:
            raise ValueError(f"Session {session_id} not found")

        problem = db.query(Problem).filter(Problem.id == session.problem_id).first()
        if not problem:
            raise ValueError(f"Problem for session {session_id} not found")

        events = (
            db.query(EventLog)
            .filter(EventLog.session_id == session_id)
            .order_by(EventLog.event_timestamp)
            .all()
        )

        performance_level = self._calculate_performance_level(session, events)
        highest_layer = self._get_highest_layer_reached(session, events)
        used_reveal = session.used_full_solution
        confusion_analysis = self._analyze_confusion(session, events)
        topic = self._get_topic_label(problem)
        time_pacing = self._calculate_time_pacing(session)

        insights = self._build_insights(highest_layer, used_reveal, confusion_analysis, time_pacing)
        recommendation = self._generate_recommendation(
            performance_level, highest_layer, confusion_analysis, topic
        )
        headline = self._generate_headline(performance_level, topic)

        return {
            "headline": headline,
            "performance_level": performance_level,
            "insights": insights,
            "recommendation": recommendation,
        }

    def _calculate_performance_level(self, session: HintSession, events: list[EventLog]) -> str:
        """Determine overall performance level."""
        if session.status == SessionStatus.COMPLETED:
            if session.confusion_count == 0:
                return "Excellent"
            elif session.confusion_count <= 2:
                return "Good"
            else:
                return "Needs Practice"
        elif session.used_full_solution:
            return "Needs Practice"
        elif session.current_layer == HintLayer.STEP:
            return "Good"
        else:
            return "Needs Practice"

    def _get_highest_layer_reached(self, session: HintSession, events: list[EventLog]) -> str:
        """Get the highest layer the student reached."""
        layer_order = {
            "CONCEPT": 1,
            "STRATEGY": 2,
            "STEP": 3,
            "COMPLETED": 4,
        }

        reached_strategy = any(e.event_type == "reached_strategy_layer" for e in events)
        reached_step = any(e.event_type == "reached_step_layer" for e in events)

        if session.current_layer == HintLayer.COMPLETED:
            return "COMPLETED"
        elif reached_step or session.current_layer == HintLayer.STEP:
            return "STEP"
        elif reached_strategy or session.current_layer == HintLayer.STRATEGY:
            return "STRATEGY"
        else:
            return "CONCEPT"

    def _analyze_confusion(self, session: HintSession, events: list[EventLog]) -> str:
        """Analyze where confusion occurred."""
        if session.confusion_count == 0:
            return "No confusion - smooth progress"

        concept_hints = sum(1 for e in events if e.event_type == "concept_hint_given")
        strategy_hints = sum(1 for e in events if e.event_type == "strategy_hint_given")
        step_hints = sum(1 for e in events if e.event_type == "step_hint_given")

        if step_hints > strategy_hints and step_hints > concept_hints:
            return "Confusion mainly at execution steps"
        elif strategy_hints > concept_hints:
            return "Needed extra help with problem-solving strategy"
        else:
            return "Needed extra time understanding core concepts"

    def _get_topic_label(self, problem: Problem) -> str:
        """Get human-readable topic label."""
        topic_labels = {
            "linear_equation_1var": "Linear Equations",
            "linear_equation_2var": "Systems of Equations",
            "quadratic_equation": "Quadratic Equations",
            "geometry_basic": "Geometry Basics",
            "arithmetic": "Arithmetic",
            "unknown": "Math Problem Solving",
        }
        return topic_labels.get(problem.problem_type.value, "Math")

    def _calculate_time_pacing(self, session: HintSession) -> str:
        """Calculate time pacing (fast/normal/slow)."""
        if session.completed_at:
            duration_seconds = (session.completed_at - session.started_at).total_seconds()
        else:
            now = datetime.now(timezone.utc)
            started = session.started_at
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            duration_seconds = (now - started).total_seconds()

        duration_minutes = duration_seconds / 60

        if duration_minutes < 3:
            return "fast"
        elif duration_minutes < 10:
            return "normal"
        else:
            return "slow"

    def _build_insights(
        self,
        highest_layer: str,
        used_reveal: bool,
        confusion_analysis: str,
        time_pacing: str,
    ) -> list[str]:
        """Build list of insight bullet points."""
        insights = []

        layer_messages = {
            "COMPLETED": "Solved independently without revealing the solution",
            "STEP": "Reached detailed step-by-step hints",
            "STRATEGY": "Reached problem-solving strategy level",
            "CONCEPT": "Worked through foundational concepts",
        }
        insights.append(layer_messages[highest_layer])

        if used_reveal:
            insights.append("Used solution reveal to understand the complete answer")

        insights.append(confusion_analysis)

        pacing_messages = {
            "fast": "Completed quickly, showing good familiarity",
            "normal": "Worked at a steady, appropriate pace",
            "slow": "Took time to work through carefully",
        }
        insights.append(pacing_messages[time_pacing])

        return insights

    def _generate_recommendation(
        self,
        performance_level: str,
        highest_layer: str,
        confusion_analysis: str,
        topic: str,
    ) -> str:
        """Generate actionable recommendation."""
        if performance_level == "Excellent":
            return f"Great work! Ready for more challenging {topic} problems."

        if performance_level == "Good":
            if "execution steps" in confusion_analysis:
                return f"Practice similar {topic} problems to build confidence with step-by-step execution."
            else:
                return f"Continue practicing {topic} to reinforce understanding."

        if highest_layer == "CONCEPT":
            return f"Review {topic} fundamentals before attempting similar problems."
        elif "strategy" in confusion_analysis.lower():
            return f"Focus on identifying problem-solving approaches in {topic}."
        else:
            return f"Work through more guided {topic} examples to build skills."

    def _generate_headline(self, performance_level: str, topic: str) -> str:
        """Generate summary headline."""
        level_adjectives = {
            "Excellent": "Excellent progress",
            "Good": "Good progress",
            "Needs Practice": "Making progress",
        }
        adjective = level_adjectives[performance_level]
        return f"{adjective} on {topic}"
