"""Email preference model for managing email subscription preferences."""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime

from backend.models.base import BaseModel, utc_now


class EmailPreference(BaseModel):
    """Store email subscription preferences for parent emails."""

    __tablename__ = "email_preferences"

    email = Column(String(255), nullable=False, unique=True, index=True)
    session_reports_enabled = Column(Boolean, nullable=False, default=True)
    weekly_digest_enabled = Column(Boolean, nullable=False, default=True)
    unsubscribe_token = Column(String(36), nullable=False, unique=True, index=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    def __repr__(self) -> str:
        return f"<EmailPreference(email='{self.email}', session_reports={self.session_reports_enabled}, weekly_digest={self.weekly_digest_enabled})>"

    @staticmethod
    def generate_token() -> str:
        """Generate a secure unsubscribe token."""
        return str(uuid.uuid4())
