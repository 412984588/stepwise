"""Pydantic schemas for stats endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from backend.models.enums import HintLayer, SessionStatus


class StatsSummary(BaseModel):
    total_sessions: int
    completed_sessions: int
    revealed_sessions: int
    active_sessions: int
    completion_rate: float
    avg_layers_to_complete: Optional[float]


class SessionListItem(BaseModel):
    session_id: str
    problem_text: str
    status: SessionStatus
    final_layer: HintLayer
    confusion_count: int
    used_full_solution: bool
    started_at: datetime
    completed_at: Optional[datetime]


class SessionListResponse(BaseModel):
    sessions: list[SessionListItem]
    total: int
    limit: int
    offset: int


class ProblemTypeStats(BaseModel):
    type: str
    label: str
    total: int
    completed: int
    revealed: int
    completion_rate: float


class EncouragementMessage(BaseModel):
    streak_message: str
    performance_message: str


class DashboardResponse(BaseModel):
    total_learning_days: int
    independent_completion_rate: float
    sessions_this_week: int
    learning_streak: int
    avg_confusion_count: Optional[float]
    avg_layers_to_complete: Optional[float]
    problem_type_stats: list[ProblemTypeStats]
    recent_sessions: list[SessionListItem]
    first_session_date: Optional[datetime]
    last_session_date: Optional[datetime]
    encouragement: EncouragementMessage


class DailyStats(BaseModel):
    date: str
    total: int
    completed: int
    revealed: int


class TrendDataResponse(BaseModel):
    daily_stats: list[DailyStats]
    period_days: int


class LearningGoal(BaseModel):
    daily_target: int
    weekly_target: int


class LearningGoalProgress(BaseModel):
    daily_target: int
    daily_completed: int
    daily_progress: float
    weekly_target: int
    weekly_completed: int
    weekly_progress: float
