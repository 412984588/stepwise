"""Event logging service for tracking learning signals."""

from typing import Any

from sqlalchemy.orm import Session

from backend.models.event_log import EventLog


class EventLogger:
    """Service for logging learning signal events."""

    def log_event(
        self,
        db: Session,
        session_id: str | None,
        event_type: str,
        details: dict[str, Any] | None = None,
    ) -> EventLog:
        """Log a learning signal event.

        Args:
            db: Database session
            session_id: Session ID (nullable for global events)
            event_type: Type of event (e.g., 'session_started', 'concept_hint_given')
            details: Optional JSON details about the event

        Returns:
            Created EventLog instance
        """
        event_log = EventLog(
            session_id=session_id,
            event_type=event_type,
            details=details,
        )
        db.add(event_log)
        db.flush()
        return event_log
