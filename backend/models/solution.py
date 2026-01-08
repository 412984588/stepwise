from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class FullSolution(BaseModel):
    __tablename__ = "full_solutions"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    steps = Column(JSON, nullable=False, default=list)
    final_answer = Column(String(500), nullable=False)
    explanation = Column(String(2000), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    problem = relationship("Problem", back_populates="solutions")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "problem_id": self.problem_id,
            "steps": self.steps,
            "final_answer": self.final_answer,
            "explanation": self.explanation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
