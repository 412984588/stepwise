from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel
from backend.models.enums import HintLayer


class HintContent(BaseModel):
    __tablename__ = "hint_contents"

    session_id = Column(String(36), ForeignKey("hint_sessions.id"), nullable=False)
    layer = Column(SQLEnum(HintLayer), nullable=False)
    sequence = Column(Integer, nullable=False, default=1)
    content = Column(Text, nullable=False)
    is_downgrade = Column(Boolean, nullable=False, default=False)

    session = relationship("HintSession", backref="hints")
