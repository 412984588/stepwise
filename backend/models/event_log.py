"""Event log model for tracking learning signals."""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import JSON

from backend.models.base import BaseModel, utc_now


class EventLog(BaseModel):
    """Tracks learning signal events throughout a session.

    Events include:
    - session_started: When a new session begins
    - concept_hint_given: When a concept layer hint is generated
    - strategy_hint_given: When a strategy layer hint is generated
    - step_hint_given: When a step layer hint is generated
    - reached_strategy_layer: When student advances to strategy layer
    - reached_step_layer: When student advances to step layer
    - reveal_used: When student reveals the full solution
    - session_completed: When student completes the session independently
    """

    __tablename__ = "event_logs"

    session_id = Column(String(36), ForeignKey("hint_sessions.id"), nullable=True)
    event_type = Column(String(50), nullable=False)
    event_timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    details = Column(JSON, nullable=True)
