from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.session import HintSession
from backend.models.event_log import EventLog
from backend.models.enums import HintLayer, SessionStatus
from backend.models.problem import Problem


class WeeklyDigestGenerator:
    def generate_weekly_digest(
        self, db: Session, email: str, start_date: datetime, end_date: datetime
    ) -> Optional[Dict]:
        sessions = self._get_sessions_for_email(db, email, start_date, end_date)

        if not sessions:
            return None

        stats = self._calculate_statistics(db, sessions)
        performance_level = self._calculate_performance_level(stats)
        recommendations = self._generate_recommendations(stats)

        return {
            "email": email,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_sessions": stats["total_sessions"],
            "completed_sessions": stats["completed_sessions"],
            "highest_layer_reached": stats["highest_layer_reached"],
            "total_time_minutes": stats["total_time_minutes"],
            "reveal_usage_count": stats["reveal_usage_count"],
            "most_challenging_topic": stats["most_challenging_topic"],
            "performance_level": performance_level,
            "recommendations": recommendations,
            "sessions": [
                {
                    "session_id": s.id,
                    "problem_type": s.problem.problem_type,
                    "started_at": s.started_at.isoformat(),
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                    "final_layer": s.current_layer.value,
                    "used_solution": s.used_full_solution,
                }
                for s in sessions[:10]
            ],
        }

    def _get_sessions_for_email(
        self, db: Session, email: str, start_date: datetime, end_date: datetime
    ) -> List[HintSession]:
        return (
            db.query(HintSession)
            .filter(
                HintSession.parent_email == email,
                HintSession.started_at >= start_date,
                HintSession.started_at <= end_date,
            )
            .order_by(HintSession.started_at.desc())
            .all()
        )

    def _calculate_statistics(self, db: Session, sessions: List[HintSession]) -> Dict:
        total_sessions = len(sessions)
        completed_sessions = sum(1 for s in sessions if s.status == SessionStatus.COMPLETED)

        highest_layer = HintLayer.CONCEPT
        for session in sessions:
            if (
                session.current_layer == HintLayer.STEP
                or session.current_layer == HintLayer.COMPLETED
            ):
                highest_layer = HintLayer.STEP
                break
            elif session.current_layer == HintLayer.STRATEGY:
                highest_layer = HintLayer.STRATEGY

        total_time_seconds = 0
        for session in sessions:
            if session.completed_at and session.started_at:
                duration = (session.completed_at - session.started_at).total_seconds()
                total_time_seconds += duration
        total_time_minutes = int(total_time_seconds / 60)

        reveal_usage_count = sum(1 for s in sessions if s.used_full_solution)

        problem_types_with_confusion = []
        for session in sessions:
            if session.confusion_count >= 2:
                problem_types_with_confusion.append(session.problem.problem_type)

        most_challenging_topic = "N/A"
        if problem_types_with_confusion:
            from collections import Counter

            topic_counts = Counter(problem_types_with_confusion)
            most_common_topic, _ = topic_counts.most_common(1)[0]
            most_challenging_topic = self._format_problem_type(most_common_topic)

        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "highest_layer_reached": highest_layer.value,
            "total_time_minutes": total_time_minutes,
            "reveal_usage_count": reveal_usage_count,
            "most_challenging_topic": most_challenging_topic,
            "completion_rate": completed_sessions / total_sessions if total_sessions > 0 else 0,
            "reveal_rate": reveal_usage_count / total_sessions if total_sessions > 0 else 0,
            "avg_confusion": sum(s.confusion_count for s in sessions) / total_sessions
            if total_sessions > 0
            else 0,
        }

    def _calculate_performance_level(self, stats: Dict) -> str:
        completion_rate = stats["completion_rate"]
        reveal_rate = stats["reveal_rate"]
        highest_layer = stats["highest_layer_reached"]

        if completion_rate >= 0.7 and reveal_rate <= 0.2 and highest_layer == "step":
            return "Excellent"
        elif completion_rate >= 0.5 and reveal_rate <= 0.4:
            return "Good"
        else:
            return "Needs Practice"

    def _generate_recommendations(self, stats: Dict) -> List[str]:
        recommendations = []

        completion_rate = stats["completion_rate"]
        reveal_rate = stats["reveal_rate"]
        avg_confusion = stats["avg_confusion"]
        most_challenging = stats["most_challenging_topic"]

        if completion_rate < 0.5:
            recommendations.append(
                "Try to complete more problems independently before moving to the next one."
            )

        if reveal_rate > 0.3:
            recommendations.append(
                "Take time to work through each hint layer before revealing the solution."
            )

        if avg_confusion > 2:
            recommendations.append(
                "Don't hesitate to review the basics before tackling harder problems."
            )

        if most_challenging != "N/A":
            recommendations.append(
                f"Focus on practicing more {most_challenging} problems to build confidence."
            )

        if completion_rate >= 0.7:
            recommendations.append("Great progress! Keep up the consistent practice routine.")

        if not recommendations:
            recommendations.append(
                "Continue practicing regularly to build strong problem-solving skills."
            )

        return recommendations[:2]

    def _format_problem_type(self, problem_type: str) -> str:
        type_mapping = {
            "linear_equation_1var": "Linear Equations",
            "linear_equation_2var": "Systems of Equations",
            "quadratic_equation": "Quadratic Equations",
            "geometry_basic": "Basic Geometry",
            "arithmetic": "Arithmetic",
        }
        return type_mapping.get(problem_type, problem_type.replace("_", " ").title())
