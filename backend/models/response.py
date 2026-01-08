from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel
from backend.models.enums import HintLayer, UnderstandingLevel


class StudentResponse(BaseModel):
    __tablename__ = "student_responses"

    session_id = Column(String(36), ForeignKey("hint_sessions.id"), nullable=False)
    layer = Column(SQLEnum(HintLayer), nullable=False)
    char_count = Column(Integer, nullable=False)
    understanding_level = Column(SQLEnum(UnderstandingLevel), nullable=False)
    keywords_matched = Column(JSON, nullable=True)

    session = relationship("HintSession", backref="responses")
