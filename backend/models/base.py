"""Base model class with common fields."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.sqlite import JSON

from backend.database.engine import Base


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)


class BaseModel(Base):
    """Abstract base model with common fields.

    All models should inherit from this class to get:
    - id: UUID primary key
    - created_at: Auto-set creation timestamp
    """

    __abstract__ = True

    id = Column(String(36), primary_key=True, default=generate_uuid)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
