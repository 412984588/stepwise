"""Email throttle model for per-email rate limiting."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Index

from backend.models.base import BaseModel, utc_now


class EmailThrottle(BaseModel):
    """
    Track email sends per email address for rate limiting.

    Used to prevent abuse even if IP addresses rotate.
    """

    __tablename__ = "email_throttles"

    email = Column(String(255), nullable=False, index=True)
    email_type = Column(String(50), nullable=False, index=True)  # session_report or weekly_digest
    window_start = Column(DateTime(timezone=True), nullable=False, index=True)
    send_count = Column(Integer, nullable=False, default=1)
    last_send_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        # Index for quick lookups
        Index("idx_email_type_window", "email", "email_type", "window_start"),
        {"sqlite_autoincrement": True},
    )

    def __repr__(self) -> str:
        return f"<EmailThrottle(email='{self.email}', type={self.email_type}, count={self.send_count})>"
