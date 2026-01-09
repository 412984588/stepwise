"""Feedback statistics endpoint for beta analytics."""

import csv
from io import StringIO
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database.engine import get_db
from backend.models.feedback import FeedbackItem

router = APIRouter()


@router.get("/stats")
def get_feedback_stats(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Get aggregated feedback statistics for beta analytics.

    Returns:
        - total_count: Total feedback submissions
        - pmf_score: Percentage of users who selected "very_disappointed"
        - pmf_breakdown: Count by each PMF answer
        - grade_breakdown: Count by grade level
        - would_pay_breakdown: Count by payment willingness
        - email_opt_in_rate: Percentage who provided email
    """
    total_count = db.query(func.count(FeedbackItem.id)).scalar() or 0

    if total_count == 0:
        return {
            "total_count": 0,
            "pmf_score": 0.0,
            "pmf_breakdown": {
                "very_disappointed": 0,
                "somewhat_disappointed": 0,
                "not_disappointed": 0,
            },
            "grade_breakdown": {},
            "would_pay_breakdown": {},
            "email_opt_in_rate": 0.0,
        }

    # PMF breakdown
    pmf_breakdown = {}
    pmf_results = (
        db.query(FeedbackItem.pmf_answer, func.count(FeedbackItem.id))
        .group_by(FeedbackItem.pmf_answer)
        .all()
    )
    for answer, count in pmf_results:
        pmf_breakdown[answer] = count

    # Calculate PMF score (% very disappointed)
    very_disappointed_count = pmf_breakdown.get("very_disappointed", 0)
    pmf_score = (very_disappointed_count / total_count) * 100 if total_count > 0 else 0.0

    # Grade breakdown
    grade_breakdown = {}
    grade_results = (
        db.query(FeedbackItem.grade_level, func.count(FeedbackItem.id))
        .group_by(FeedbackItem.grade_level)
        .all()
    )
    for grade, count in grade_results:
        grade_breakdown[grade] = count

    # Would pay breakdown
    would_pay_breakdown = {}
    would_pay_results = (
        db.query(FeedbackItem.would_pay, func.count(FeedbackItem.id))
        .filter(FeedbackItem.would_pay.isnot(None))
        .group_by(FeedbackItem.would_pay)
        .all()
    )
    for answer, count in would_pay_results:
        would_pay_breakdown[answer] = count

    # Email opt-in rate
    email_count = (
        db.query(func.count(FeedbackItem.id)).filter(FeedbackItem.email.isnot(None)).scalar() or 0
    )
    email_opt_in_rate = (email_count / total_count) * 100 if total_count > 0 else 0.0

    return {
        "total_count": total_count,
        "pmf_score": round(pmf_score, 1),
        "pmf_breakdown": pmf_breakdown,
        "grade_breakdown": grade_breakdown,
        "would_pay_breakdown": would_pay_breakdown,
        "email_opt_in_rate": round(email_opt_in_rate, 1),
    }


@router.get("/list")
def get_feedback_list(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Get paginated list of feedback items (most recent first).

    Args:
        limit: Max items to return (default 50, max 100)
        offset: Number of items to skip (default 0)

    Returns:
        - items: List of feedback items
        - total: Total count
        - has_more: Whether there are more items
    """
    if limit > 100:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 100")

    total = db.query(func.count(FeedbackItem.id)).scalar() or 0

    items = (
        db.query(FeedbackItem)
        .order_by(FeedbackItem.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return {
        "items": [
            {
                "id": item.id,
                "created_at": item.created_at.isoformat(),
                "grade_level": item.grade_level,
                "pmf_answer": item.pmf_answer,
                "would_pay": item.would_pay,
                "what_worked": item.what_worked,
                "what_confused": item.what_confused,
                "email": item.email,
                "locale": item.locale,
            }
            for item in items
        ],
        "total": total,
        "has_more": (offset + limit) < total,
    }


@router.get("/export")
def export_feedback_csv(db: Session = Depends(get_db)) -> StreamingResponse:
    """Export all feedback items as CSV file.

    Returns:
        CSV file with all feedback data
    """
    items = db.query(FeedbackItem).order_by(FeedbackItem.created_at.desc()).all()

    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "ID",
            "Created At",
            "Grade Level",
            "PMF Answer",
            "Would Pay",
            "What Worked",
            "What Confused",
            "Email",
            "Locale",
        ]
    )

    # Rows
    for item in items:
        writer.writerow(
            [
                item.id,
                item.created_at.isoformat(),
                item.grade_level,
                item.pmf_answer,
                item.would_pay or "",
                item.what_worked or "",
                item.what_confused or "",
                item.email or "",
                item.locale,
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=feedback_export.csv"},
    )
