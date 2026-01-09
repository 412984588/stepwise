"""Feedback API endpoints for beta user feedback collection."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

from backend.database.engine import get_db
from backend.models.feedback import FeedbackItem

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    """Request schema for submitting feedback."""

    pmf_answer: str  # very_disappointed, somewhat_disappointed, not_disappointed
    grade_level: str  # grade_4 through grade_9
    locale: str = "en-US"
    would_pay: Optional[str] = None
    what_worked: Optional[str] = None
    what_confused: Optional[str] = None
    email: Optional[str] = None

    @field_validator("pmf_answer")
    @classmethod
    def validate_pmf_answer(cls, v: str) -> str:
        valid = ["very_disappointed", "somewhat_disappointed", "not_disappointed"]
        if v not in valid:
            raise ValueError(f"pmf_answer must be one of: {valid}")
        return v

    @field_validator("grade_level")
    @classmethod
    def validate_grade_level(cls, v: str) -> str:
        valid = ["grade_4", "grade_5", "grade_6", "grade_7", "grade_8", "grade_9"]
        if v not in valid:
            raise ValueError(f"grade_level must be one of: {valid}")
        return v

    @field_validator("would_pay")
    @classmethod
    def validate_would_pay(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        valid = [
            "yes_definitely",
            "yes_probably",
            "not_sure",
            "probably_not",
            "definitely_not",
        ]
        if v not in valid:
            raise ValueError(f"would_pay must be one of: {valid}")
        return v

    @field_validator("what_worked", "what_confused")
    @classmethod
    def validate_text_length(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if len(v) > 500:
            return v[:500]
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        # Basic email validation
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v


class FeedbackResponse(BaseModel):
    """Response schema for feedback submission."""

    id: str
    message: str


@router.post("", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)) -> FeedbackResponse:
    """
    Submit beta user feedback.

    This endpoint collects feedback from beta users including:
    - PMF (Product-Market Fit) question response
    - What worked well
    - What was confusing
    - Payment intent
    - Child's grade level
    - Optional parent email for follow-up

    Privacy notes:
    - No child names or identifiers are collected
    - No raw student responses are stored
    - Email is optional and only used for product research
    """
    feedback = FeedbackItem(
        locale=request.locale,
        grade_level=request.grade_level,
        pmf_answer=request.pmf_answer,
        would_pay=request.would_pay,
        what_worked=request.what_worked,
        what_confused=request.what_confused,
        email=request.email,
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return FeedbackResponse(id=feedback.id, message="Thank you for your feedback!")
