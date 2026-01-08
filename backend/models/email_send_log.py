"""Email send log model for idempotency and audit trail."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Index, UniqueConstraint, Date
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from enum import Enum

from backend.models.base import BaseModel, utc_now


class EmailType(str, Enum):
    """Types of emails sent by the system."""

    SESSION_REPORT = "session_report"
    WEEKLY_DIGEST = "weekly_digest"


class EmailSendStatus(str, Enum):
    """Status of email send operation."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class EmailSendLog(BaseModel):
    """
    Log of all email send attempts for idempotency and audit.

    Idempotency rules:
    - Session report: At most ONE successful send per (email, session_id)
    - Weekly digest: At most ONE successful send per (email, week_start_date)
    """

    __tablename__ = "email_send_logs"

    email = Column(String(255), nullable=False, index=True)
    email_type = Column(String(50), nullable=False, index=True)  # EmailType enum
    session_id = Column(String(36), nullable=True, index=True)  # For session reports
    week_start_date = Column(Date, nullable=True, index=True)  # For weekly digests
    idempotency_key = Column(String(255), nullable=False, unique=True, index=True)
    status = Column(String(20), nullable=False, default=EmailSendStatus.PENDING.value)
    error_message = Column(String(500), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        Index("idx_email_type_status", "email", "email_type", "status"),
        {"sqlite_autoincrement": True},
    )

    def __repr__(self) -> str:
        return f"<EmailSendLog(email='{self.email}', type={self.email_type}, status={self.status})>"

    @staticmethod
    def generate_idempotency_key(
        email: str,
        email_type: EmailType,
        session_id: str | None = None,
        week_start_date: str | None = None,
    ) -> str:
        """
        Generate idempotency key for email sends.

        Args:
            email: Recipient email
            email_type: Type of email
            session_id: Session ID (for session reports)
            week_start_date: Week start date string YYYY-MM-DD (for weekly digests)

        Returns:
            Idempotency key string
        """
        if email_type == EmailType.SESSION_REPORT:
            return f"session_report:{email}:{session_id}"
        elif email_type == EmailType.WEEKLY_DIGEST:
            return f"weekly_digest:{email}:{week_start_date}"
        else:
            raise ValueError(f"Unknown email type: {email_type}")
