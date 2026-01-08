from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel, utc_now
from backend.models.enums import HintLayer, SessionStatus


class HintSession(BaseModel):
    __tablename__ = "hint_sessions"

    problem_id = Column(String(36), ForeignKey("problems.id"), nullable=False)
    current_layer = Column(SQLEnum(HintLayer), nullable=False, default=HintLayer.CONCEPT)
    status = Column(SQLEnum(SessionStatus), nullable=False, default=SessionStatus.ACTIVE)
    confusion_count = Column(Integer, nullable=False, default=0)
    used_full_solution = Column(Boolean, nullable=False, default=False)
    parent_email = Column(String(255), nullable=True)
    session_access_token = Column(
        String(36), nullable=True, index=True
    )  # For user-facing endpoints
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_active_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    problem = relationship("Problem", backref="sessions")

    def touch(self) -> None:
        self.last_active_at = datetime.now(timezone.utc)

    @staticmethod
    def generate_access_token() -> str:
        """Generate a secure session access token."""
        return str(uuid.uuid4())
