from sqlalchemy import Column, String, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel
from backend.models.enums import ProblemType, Difficulty


class Problem(BaseModel):
    __tablename__ = "problems"

    raw_text = Column(String(500), nullable=False)
    problem_type = Column(SQLEnum(ProblemType), nullable=False, default=ProblemType.UNKNOWN)
    difficulty = Column(SQLEnum(Difficulty), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)

    solutions = relationship("FullSolution", back_populates="problem")
