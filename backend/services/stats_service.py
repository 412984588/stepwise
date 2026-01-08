"""Service for calculating and retrieving learning statistics."""

from datetime import datetime, timezone, timedelta
from sqlalchemy import func, distinct, case
from sqlalchemy.orm import Session

from backend.models.enums import HintLayer, SessionStatus, ProblemType
from backend.models.session import HintSession
from backend.models.problem import Problem
from backend.schemas.stats import (
    StatsSummary,
    SessionListItem,
    DashboardResponse,
    ProblemTypeStats,
    EncouragementMessage,
    DailyStats,
    TrendDataResponse,
    LearningGoalProgress,
)


PROBLEM_TYPE_LABELS = {
    ProblemType.LINEAR_EQUATION_1VAR: "一元一次方程",
    ProblemType.LINEAR_EQUATION_2VAR: "二元一次方程组",
    ProblemType.QUADRATIC_EQUATION: "一元二次方程",
    ProblemType.GEOMETRY_BASIC: "基础几何",
    ProblemType.ARITHMETIC: "四则运算",
    ProblemType.UNKNOWN: "其他",
}


class StatsService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_summary(self) -> StatsSummary:
        total = self._db.query(HintSession).count()

        if total == 0:
            return StatsSummary(
                total_sessions=0,
                completed_sessions=0,
                revealed_sessions=0,
                active_sessions=0,
                completion_rate=0.0,
                avg_layers_to_complete=None,
            )

        completed = (
            self._db.query(HintSession)
            .filter(HintSession.status == SessionStatus.COMPLETED)
            .count()
        )

        revealed = (
            self._db.query(HintSession).filter(HintSession.status == SessionStatus.REVEALED).count()
        )

        active = (
            self._db.query(HintSession).filter(HintSession.status == SessionStatus.ACTIVE).count()
        )

        completion_rate = ((completed + revealed) / total) * 100

        avg_layers = self._calculate_avg_layers()

        return StatsSummary(
            total_sessions=total,
            completed_sessions=completed,
            revealed_sessions=revealed,
            active_sessions=active,
            completion_rate=round(completion_rate, 1),
            avg_layers_to_complete=avg_layers,
        )

    def list_sessions(self, limit: int = 20, offset: int = 0) -> list[SessionListItem]:
        sessions = (
            self._db.query(HintSession)
            .order_by(HintSession.started_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [
            SessionListItem(
                session_id=session.id,
                problem_text=session.problem.raw_text,
                status=session.status,
                final_layer=session.current_layer,
                confusion_count=session.confusion_count,
                used_full_solution=session.used_full_solution,
                started_at=session.started_at,
                completed_at=session.completed_at,
            )
            for session in sessions
        ]

    def count_sessions(self) -> int:
        return self._db.query(HintSession).count()

    def _calculate_avg_layers(self) -> float | None:
        finished_sessions = (
            self._db.query(HintSession)
            .filter(HintSession.status.in_([SessionStatus.COMPLETED, SessionStatus.REVEALED]))
            .all()
        )

        if not finished_sessions or len(finished_sessions) == 0:
            return None

        total_layers = sum(
            self._layer_to_number(session.current_layer) for session in finished_sessions
        )

        return round(total_layers / len(finished_sessions), 1)

    def _layer_to_number(self, layer: HintLayer) -> int:
        mapping = {
            HintLayer.CONCEPT: 1,
            HintLayer.STRATEGY: 2,
            HintLayer.STEP: 3,
            HintLayer.COMPLETED: 4,
            HintLayer.REVEALED: 4,
        }
        return mapping.get(layer, 0)

    def get_dashboard(self) -> DashboardResponse:
        total_learning_days = self._get_total_learning_days()
        completed, revealed = self._get_completion_counts()
        independent_rate = self._calc_independent_rate(completed, revealed)
        sessions_this_week = self._get_sessions_this_week()
        learning_streak = self._get_learning_streak()
        avg_confusion = self._get_avg_confusion()
        avg_layers = self._calculate_avg_layers()
        problem_stats = self._get_problem_type_stats()
        recent = self.list_sessions(limit=5, offset=0)
        first_date, last_date = self._get_date_range()
        encouragement = self._generate_encouragement(learning_streak, independent_rate)

        return DashboardResponse(
            total_learning_days=total_learning_days,
            independent_completion_rate=independent_rate,
            sessions_this_week=sessions_this_week,
            learning_streak=learning_streak,
            avg_confusion_count=avg_confusion,
            avg_layers_to_complete=avg_layers,
            problem_type_stats=problem_stats,
            recent_sessions=recent,
            first_session_date=first_date,
            last_session_date=last_date,
            encouragement=encouragement,
        )

    def _get_total_learning_days(self) -> int:
        result = self._db.query(func.count(distinct(func.date(HintSession.started_at)))).scalar()
        return result or 0

    def _get_completion_counts(self) -> tuple[int, int]:
        completed = (
            self._db.query(HintSession)
            .filter(HintSession.status == SessionStatus.COMPLETED)
            .count()
        )
        revealed = (
            self._db.query(HintSession).filter(HintSession.status == SessionStatus.REVEALED).count()
        )
        return completed, revealed

    def _calc_independent_rate(self, completed: int, revealed: int) -> float:
        total = completed + revealed
        if total == 0:
            return 0.0
        return round((completed / total) * 100, 1)

    def _get_sessions_this_week(self) -> int:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        return self._db.query(HintSession).filter(HintSession.started_at >= week_ago).count()

    def _get_learning_streak(self) -> int:
        dates = (
            self._db.query(func.date(HintSession.started_at))
            .distinct()
            .order_by(func.date(HintSession.started_at).desc())
            .all()
        )

        if not dates:
            return 0

        today = datetime.now(timezone.utc).date()
        streak = 0
        expected_date = today

        for (session_date,) in dates:
            if session_date == expected_date:
                streak += 1
                expected_date = expected_date - timedelta(days=1)
            elif session_date == expected_date + timedelta(days=1):
                expected_date = session_date
                streak += 1
                expected_date = expected_date - timedelta(days=1)
            else:
                break

        return streak

    def _get_avg_confusion(self) -> float | None:
        result = self._db.query(func.avg(HintSession.confusion_count)).scalar()
        if result is None:
            return None
        return round(float(result), 1)

    def _get_problem_type_stats(self) -> list[ProblemTypeStats]:
        results = (
            self._db.query(
                Problem.problem_type,
                func.count(HintSession.id).label("total"),
                func.sum(case((HintSession.status == SessionStatus.COMPLETED, 1), else_=0)).label(
                    "completed"
                ),
                func.sum(case((HintSession.status == SessionStatus.REVEALED, 1), else_=0)).label(
                    "revealed"
                ),
            )
            .join(HintSession, HintSession.problem_id == Problem.id)
            .group_by(Problem.problem_type)
            .all()
        )

        stats = []
        for row in results:
            total = row.total or 0
            completed = row.completed or 0
            revealed = row.revealed or 0
            rate = (
                round((completed / (completed + revealed)) * 100, 1)
                if (completed + revealed) > 0
                else 0.0
            )

            stats.append(
                ProblemTypeStats(
                    type=row.problem_type.value,
                    label=PROBLEM_TYPE_LABELS.get(row.problem_type, "其他"),
                    total=total,
                    completed=completed,
                    revealed=revealed,
                    completion_rate=rate,
                )
            )

        return sorted(stats, key=lambda x: x.total, reverse=True)

    def _get_date_range(self) -> tuple[datetime | None, datetime | None]:
        first = self._db.query(func.min(HintSession.started_at)).scalar()
        last = self._db.query(func.max(HintSession.started_at)).scalar()
        return first, last

    def _generate_encouragement(self, streak: int, rate: float) -> EncouragementMessage:
        if streak >= 7:
            streak_msg = "太棒了！连续学习一周！🎉"
        elif streak >= 3:
            streak_msg = f"已经连续学习 {streak} 天了，继续保持！"
        elif streak == 1:
            streak_msg = "今天又来学习了，很棒！"
        else:
            streak_msg = "今天开始新的学习之旅吧！"

        if rate >= 80:
            perf_msg = "独立完成率很高，继续保持！💪"
        elif rate >= 50:
            perf_msg = "正在稳步进步中！"
        elif rate > 0:
            perf_msg = "多思考一下，你可以的！"
        else:
            perf_msg = "开始你的第一道题吧！"

        return EncouragementMessage(
            streak_message=streak_msg,
            performance_message=perf_msg,
        )
