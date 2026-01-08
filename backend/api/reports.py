"""PDF report generation API endpoints."""

import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from backend.database.engine import get_db
from backend.models import HintSession, Problem, EventLog, HintLayer
from backend.schemas.errors import ErrorResponse
from backend.services.learning_summary import LearningSummaryGenerator
from backend.services.rate_limiter import get_reports_rate_limiter
from backend.i18n import get_message
from backend.utils.validation import validate_session_id
from backend.api.dependencies import verify_api_key, verify_session_access, check_rate_limit

router = APIRouter()


@router.get(
    "/session/{session_id}/pdf",
    responses={
        200: {"description": "PDF report generated successfully"},
        404: {"model": ErrorResponse},
    },
)
def get_session_pdf_report(
    session_id: str,
    hint_session: HintSession = Depends(verify_session_access),
    db: Session = Depends(get_db),
    _rate_limit: None = Depends(check_rate_limit(get_reports_rate_limiter())),
) -> Response:
    """Generate and download a PDF report for a session.

    Requires X-Session-Access-Token header.

    Args:
        session_id: The session ID to generate report for
        hint_session: Session object (validated by verify_session_access)
        db: Database session

    Returns:
        PDF file as binary response

    Raises:
        HTTPException: If session not found or token invalid
    """
    # Session already validated by verify_session_access dependency
    # No need to query again

    problem = db.query(Problem).filter(Problem.id == hint_session.problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=404,
            detail={"error": "PROBLEM_NOT_FOUND", "message": get_message("PROBLEM_NOT_FOUND")},
        )

    # Fetch event logs
    events = (
        db.query(EventLog)
        .filter(EventLog.session_id == session_id)
        .order_by(EventLog.event_timestamp)
        .all()
    )

    # Generate learning summary
    summary_generator = LearningSummaryGenerator()
    try:
        summary = summary_generator.generate_session_summary(db, session_id)
    except ValueError:
        summary = None

    # Generate PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, "StepWise Session Report")

    y_position = height - 80

    # Learning Summary Section (if available)
    if summary:
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y_position, "Learning Summary for Parents")
        y_position -= 25

        p.setFont("Helvetica-Bold", 14)
        p.setFillColorRGB(0.2, 0.4, 0.8)
        p.drawString(50, y_position, summary["headline"])
        p.setFillColorRGB(0, 0, 0)
        y_position -= 20

        p.setFont("Helvetica", 11)
        p.drawString(50, y_position, f"Performance: {summary['performance_level']}")
        y_position -= 25

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, "Key Insights:")
        y_position -= 18

        p.setFont("Helvetica", 10)
        for insight in summary["insights"]:
            p.drawString(70, y_position, f"• {insight}")
            y_position -= 15

        y_position -= 10
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, "Recommendation:")
        y_position -= 18

        p.setFont("Helvetica", 10)
        p.drawString(70, y_position, summary["recommendation"])
        y_position -= 30

        p.line(50, y_position, width - 50, y_position)
        y_position -= 20
    else:
        y_position = height - 80

    # Session ID and metadata
    p.setFont("Helvetica", 10)
    p.drawString(50, y_position, f"Session ID: {session_id}")
    y_position -= 15
    p.drawString(
        50, y_position, f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )
    y_position -= 25

    # Problem text
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "Problem:")
    y_position -= 20
    p.setFont("Helvetica", 12)
    p.drawString(50, y_position, problem.raw_text[:80])
    y_position -= 30

    # Session details
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "Session Details:")
    y_position -= 20
    p.setFont("Helvetica", 11)
    p.drawString(70, y_position, f"Status: {hint_session.status.value.upper()}")
    y_position -= 20
    p.drawString(70, y_position, f"Final Layer: {hint_session.current_layer.value.upper()}")
    y_position -= 20
    p.drawString(70, y_position, f"Confusion Count: {hint_session.confusion_count}")
    y_position -= 20
    p.drawString(
        70, y_position, f"Used Full Solution: {'Yes' if hint_session.used_full_solution else 'No'}"
    )
    y_position -= 20

    # Calculate duration
    if hint_session.completed_at:
        duration = hint_session.completed_at - hint_session.started_at
        duration_minutes = int(duration.total_seconds() / 60)
        p.drawString(70, y_position, f"Duration: {duration_minutes} minutes")
    else:
        p.drawString(70, y_position, f"Duration: In progress")

    y_position -= 30

    # Layers reached
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "Layers Reached:")
    y_position -= 20
    p.setFont("Helvetica", 11)

    layer_events = {
        "CONCEPT": False,
        "STRATEGY": False,
        "STEP": False,
    }

    for event in events:
        if event.event_type == "reached_strategy_layer":
            layer_events["STRATEGY"] = True
        elif event.event_type == "reached_step_layer":
            layer_events["STEP"] = True

    # Always reached concept (session starts there)
    layer_events["CONCEPT"] = True

    for layer, reached in layer_events.items():
        status_mark = "✓" if reached else "✗"
        p.drawString(70, y_position, f"{status_mark} {layer}")
        y_position -= 18

    y_position -= 15

    # Event timeline
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position, "Event Timeline:")
    y_position -= 20
    p.setFont("Helvetica", 10)

    event_labels = {
        "session_started": "Session Started",
        "concept_hint_given": "Concept Hint Given",
        "strategy_hint_given": "Strategy Hint Given",
        "step_hint_given": "Step Hint Given",
        "reached_strategy_layer": "Advanced to Strategy Layer",
        "reached_step_layer": "Advanced to Step Layer",
        "reveal_used": "Solution Revealed",
        "session_completed": "Session Completed",
    }

    for event in events[:10]:  # Limit to first 10 events to fit on page
        timestamp = event.event_timestamp.strftime("%H:%M:%S")
        event_label = event_labels.get(event.event_type, event.event_type)
        p.drawString(70, y_position, f"{timestamp} - {event_label}")
        y_position -= 15

        if y_position < 100:  # Prevent overflow
            break

    if len(events) > 10:
        p.drawString(70, y_position, f"... and {len(events) - 10} more events")

    # Footer
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(50, 50, "StepWise - Socratic Math Tutoring System")

    # Finalize PDF
    p.showPage()
    p.save()

    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=stepwise_session_{session_id}.pdf"},
    )


@router.get(
    "/session/{session_id}/summary",
    responses={
        200: {"description": "Learning summary generated successfully"},
        404: {"model": ErrorResponse},
    },
)
def get_session_summary(
    session_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
    _rate_limit: None = Depends(check_rate_limit(get_reports_rate_limiter())),
) -> dict:
    """Generate and return a learning summary for a session.

    Args:
        session_id: The session ID to summarize
        db: Database session

    Returns:
        JSON with headline, performance_level, insights, and recommendation

    Raises:
        HTTPException: If session not found
    """
    # Validate session_id format
    validate_session_id(session_id)
    hint_session = db.query(HintSession).filter(HintSession.id == session_id).first()
    if not hint_session:
        raise HTTPException(
            status_code=404,
            detail={"error": "SESSION_NOT_FOUND", "message": get_message("SESSION_NOT_FOUND")},
        )

    generator = LearningSummaryGenerator()
    try:
        summary = generator.generate_session_summary(db, session_id)
        return summary
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail={"error": "SUMMARY_GENERATION_FAILED", "message": str(e)},
        )
