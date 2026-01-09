"""Feedback item model for beta user feedback."""

from sqlalchemy import Column, String, Text

from backend.models.base import BaseModel


class FeedbackItem(BaseModel):
    """Store beta user feedback submissions.

    Privacy notes:
    - No child names or identifiers stored
    - No raw student responses stored
    - Email is optional and only for follow-up
    """

    __tablename__ = "feedback_items"

    # Required fields
    locale = Column(String(10), nullable=False, default="en-US")
    grade_level = Column(String(20), nullable=False)  # grade_4, grade_5, etc.
    pmf_answer = Column(
        String(30), nullable=False
    )  # very_disappointed, somewhat_disappointed, not_disappointed

    # Optional fields
    would_pay = Column(
        String(30), nullable=True
    )  # yes_definitely, yes_probably, not_sure, probably_not, definitely_not
    what_worked = Column(Text, nullable=True)  # Free text, max 500 chars
    what_confused = Column(Text, nullable=True)  # Free text, max 500 chars
    email = Column(String(255), nullable=True)  # Optional parent email for follow-up
