import re
from fastapi import APIRouter, Depends, HTTPException, Header, status, Body
from sqlalchemy.orm import Session

from backend.database.engine import get_db
from backend.models import (
    Problem,
    HintSession,
    HintContent,
    StudentResponse,
    ProblemType,
    HintLayer,
    SessionStatus,
    UnderstandingLevel,
)
from backend.schemas.problem import StartSessionRequest, StartSessionResponse, SessionResponse
from backend.schemas.response import RespondRequest, RespondResponse
from backend.schemas.solution import CompleteRequest, CompleteResponse
from backend.schemas.errors import ErrorResponse
from backend.services.problem_classifier import ProblemClassifier
from backend.services.hint_generator import HintGenerator
from backend.services.understanding_evaluator import UnderstandingEvaluator
from backend.services.session_manager import SessionManager
from backend.services.event_logger import EventLogger
from backend.services import entitlements
from backend.i18n import get_message, Locale
from backend.utils.validation import generate_session_id, validate_session_id


MIN_RESPONSE_LENGTH = 10

router = APIRouter()


def is_math_problem(text: str) -> bool:
    math_indicators = [
        r"[+\-×÷*/=]",
        r"\d",
        r"[xyzXYZ]",
        r"解|求|计算|方程|面积|周长",
    ]
    for pattern in math_indicators:
        if re.search(pattern, text):
            return True
    return False


@router.post(
    "/start",
    response_model=StartSessionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        402: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
async def start_session(
    request: StartSessionRequest,
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(None, alias="X-User-ID"),
) -> StartSessionResponse:
    user_id = x_user_id
    if user_id:
        usage_status = entitlements.check_can_start_session(db, user_id)
        if not usage_status.can_start:
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "LIMIT_REACHED",
                    "message": get_message("LIMIT_REACHED", request.locale),
                    "used": usage_status.used,
                    "limit": usage_status.limit,
                },
            )

    problem_text = request.problem_text.strip()
    locale = request.locale

    if not problem_text:
        raise HTTPException(
            status_code=400,
            detail={"error": "EMPTY_INPUT", "message": get_message("EMPTY_INPUT", locale)},
        )

    if len(problem_text) > 500:
        raise HTTPException(
            status_code=400,
            detail={"error": "TOO_LONG", "message": get_message("TOO_LONG", locale)},
        )

    if not is_math_problem(problem_text):
        raise HTTPException(
            status_code=400,
            detail={"error": "NOT_MATH", "message": get_message("NOT_MATH", locale)},
        )

    classifier = ProblemClassifier()
    problem_type = classifier.classify(problem_text)

    problem = Problem(
        raw_text=problem_text,
        problem_type=problem_type,
        grade_level=request.grade_level,
    )
    db.add(problem)
    db.flush()

    session_id = generate_session_id()
    hint_session = HintSession(
        id=session_id,
        problem_id=problem.id,
        current_layer=HintLayer.CONCEPT,
        status=SessionStatus.ACTIVE,
        session_access_token=HintSession.generate_access_token(),
    )
    db.add(hint_session)
    db.flush()

    generator = HintGenerator()
    hint = generator.generate(
        problem_text=problem_text,
        problem_type=problem_type,
        layer=HintLayer.CONCEPT,
        locale=locale,
        grade_level=request.grade_level,
    )

    hint_content = HintContent(
        session_id=session_id,
        layer=HintLayer.CONCEPT,
        sequence=1,
        content=hint.content,
        is_downgrade=False,
    )
    db.add(hint_content)

    # Log events
    event_logger = EventLogger()
    event_logger.log_event(db, session_id, "session_started", {"problem_type": problem_type.value})
    event_logger.log_event(db, session_id, "concept_hint_given", {"sequence": 1})

    db.commit()

    if user_id:
        entitlements.increment_usage(db, user_id)

    return StartSessionResponse(
        session_id=session_id,
        session_access_token=hint_session.session_access_token,
        problem_type=problem_type.value.upper(),
        topic=problem.topic.value if problem.topic else None,
        current_layer=HintLayer.CONCEPT.value.upper(),
        hint_content=hint.content,
        requires_response=True,
    )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> SessionResponse:
    # Validate session_id format
    validate_session_id(session_id)

    hint_session = db.query(HintSession).filter(HintSession.id == session_id).first()

    if not hint_session:
        raise HTTPException(
            status_code=404,
            detail={"error": "SESSION_NOT_FOUND", "message": get_message("SESSION_NOT_FOUND")},
        )

    problem = db.query(Problem).filter(Problem.id == hint_session.problem_id).first()

    last_hint = (
        db.query(HintContent)
        .filter(HintContent.session_id == session_id)
        .order_by(HintContent.created_at.desc())
        .first()
    )

    completed_layers = []
    layer_order = [HintLayer.CONCEPT, HintLayer.STRATEGY, HintLayer.STEP]
    current_idx = (
        layer_order.index(hint_session.current_layer)
        if hint_session.current_layer in layer_order
        else -1
    )
    for i, layer in enumerate(layer_order):
        if i < current_idx:
            completed_layers.append(layer.value.upper())

    can_reveal = (
        hint_session.current_layer == HintLayer.STEP
        or hint_session.status == SessionStatus.COMPLETED
    )

    return SessionResponse(
        session_id=session_id,
        problem={
            "raw_text": problem.raw_text,
            "problem_type": problem.problem_type.value.upper(),
        },
        status=hint_session.status.value.upper(),
        current_layer=hint_session.current_layer.value.upper(),
        confusion_count=hint_session.confusion_count,
        layers_completed=completed_layers,
        can_reveal_solution=can_reveal,
        last_hint=last_hint.content if last_hint else None,
        started_at=hint_session.started_at.isoformat(),
        last_active_at=hint_session.last_active_at.isoformat(),
    )


@router.post(
    "/{session_id}/respond",
    response_model=RespondResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def respond_to_hint(
    session_id: str,
    request: RespondRequest,
    db: Session = Depends(get_db),
) -> RespondResponse:
    # Validate session_id format
    validate_session_id(session_id)

    hint_session = db.query(HintSession).filter(HintSession.id == session_id).first()

    if not hint_session:
        raise HTTPException(
            status_code=404,
            detail={"error": "SESSION_NOT_FOUND", "message": get_message("SESSION_NOT_FOUND")},
        )

    if hint_session.status != SessionStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail={"error": "SESSION_COMPLETED", "message": get_message("SESSION_COMPLETED")},
        )

    response_text = request.response_text.strip()

    if len(response_text) < MIN_RESPONSE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail={"error": "RESPONSE_TOO_SHORT", "message": get_message("RESPONSE_TOO_SHORT")},
        )

    problem = db.query(Problem).filter(Problem.id == hint_session.problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=404,
            detail={"error": "PROBLEM_NOT_FOUND", "message": get_message("PROBLEM_NOT_FOUND")},
        )

    evaluator = UnderstandingEvaluator()
    eval_result = evaluator.evaluate(
        response_text=response_text,
        problem_type=problem.problem_type,
        layer=hint_session.current_layer,
    )

    student_response = StudentResponse(
        session_id=session_id,
        layer=hint_session.current_layer,
        char_count=eval_result.char_count,
        understanding_level=eval_result.understanding_level,
        keywords_matched=eval_result.keywords_matched,
    )
    db.add(student_response)

    session_manager = SessionManager()
    transition = session_manager.determine_transition(
        current_layer=hint_session.current_layer,
        understanding_level=eval_result.understanding_level,
        confusion_count=hint_session.confusion_count,
    )

    previous_layer = hint_session.current_layer.value.upper()
    previous_layer_enum = hint_session.current_layer

    if transition.reset_confusion:
        hint_session.confusion_count = 0
    elif not transition.should_advance:
        hint_session.confusion_count += 1

    hint_session.current_layer = transition.new_layer
    hint_session.touch()

    if transition.new_layer == HintLayer.COMPLETED:
        hint_session.status = SessionStatus.COMPLETED

    last_hint = (
        db.query(HintContent)
        .filter(HintContent.session_id == session_id, HintContent.layer == previous_layer.lower())
        .order_by(HintContent.sequence.desc())
        .first()
    )
    current_sequence = last_hint.sequence if last_hint else 0

    generator = HintGenerator()
    new_hint = generator.generate(
        problem_text=problem.raw_text,
        problem_type=problem.problem_type,
        layer=transition.new_layer
        if transition.new_layer != HintLayer.COMPLETED
        else HintLayer.STEP,
        sequence=session_manager.get_next_sequence(current_sequence, not transition.should_advance),
        is_downgrade=transition.is_downgrade,
    )

    hint_content = HintContent(
        session_id=session_id,
        layer=transition.new_layer
        if transition.new_layer != HintLayer.COMPLETED
        else HintLayer.STEP,
        sequence=new_hint.sequence,
        content=new_hint.content,
        is_downgrade=transition.is_downgrade,
    )
    db.add(hint_content)

    # Log events
    event_logger = EventLogger()

    # Log hint given event
    if transition.new_layer == HintLayer.STRATEGY or (
        transition.should_advance and previous_layer_enum == HintLayer.CONCEPT
    ):
        event_logger.log_event(
            db, session_id, "strategy_hint_given", {"sequence": new_hint.sequence}
        )
    elif transition.new_layer == HintLayer.STEP or (
        transition.should_advance and previous_layer_enum == HintLayer.STRATEGY
    ):
        event_logger.log_event(db, session_id, "step_hint_given", {"sequence": new_hint.sequence})
    elif previous_layer_enum == HintLayer.CONCEPT and not transition.should_advance:
        event_logger.log_event(
            db, session_id, "concept_hint_given", {"sequence": new_hint.sequence}
        )

    # Log layer advancement events
    if transition.should_advance:
        if transition.new_layer == HintLayer.STRATEGY:
            event_logger.log_event(db, session_id, "reached_strategy_layer", {})
        elif transition.new_layer == HintLayer.STEP:
            event_logger.log_event(db, session_id, "reached_step_layer", {})

    db.commit()

    can_reveal = session_manager.can_reveal_solution(
        hint_session.current_layer,
        hint_session.status,
    )

    return RespondResponse(
        session_id=session_id,
        current_layer=hint_session.current_layer.value.upper(),
        previous_layer=previous_layer,
        understanding_level=eval_result.understanding_level.value.upper(),
        confusion_count=hint_session.confusion_count,
        is_downgrade=transition.is_downgrade,
        hint_content=new_hint.content,
        requires_response=hint_session.status == SessionStatus.ACTIVE,
        can_reveal_solution=can_reveal,
    )


@router.post(
    "/{session_id}/reveal",
    responses={
        200: {"description": "Solution revealed successfully"},
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def reveal_solution(
    session_id: str,
    db: Session = Depends(get_db),
) -> dict:
    from backend.schemas.solution import RevealResponse
    from backend.services.solution_generator import SolutionGenerator
    from backend.models.solution import FullSolution

    # Validate session_id format
    validate_session_id(session_id)

    hint_session = db.query(HintSession).filter(HintSession.id == session_id).first()

    if not hint_session:
        raise HTTPException(
            status_code=404,
            detail={"error": "SESSION_NOT_FOUND", "message": get_message("SESSION_NOT_FOUND")},
        )

    session_manager = SessionManager()
    if not session_manager.can_reveal_solution(hint_session.current_layer, hint_session.status):
        raise HTTPException(
            status_code=400,
            detail={"error": "REVEAL_NOT_ALLOWED", "message": get_message("REVEAL_NOT_ALLOWED")},
        )

    problem = db.query(Problem).filter(Problem.id == hint_session.problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=404,
            detail={"error": "PROBLEM_NOT_FOUND", "message": get_message("PROBLEM_NOT_FOUND")},
        )

    generator = SolutionGenerator()
    solution = generator.generate(
        problem_text=problem.raw_text,
        problem_type=problem.problem_type,
    )

    full_solution = FullSolution(
        problem_id=problem.id,
        steps=solution.steps,
        final_answer=solution.final_answer,
        explanation=solution.explanation,
    )
    db.add(full_solution)

    hint_session.status = SessionStatus.REVEALED
    hint_session.current_layer = HintLayer.REVEALED
    hint_session.used_full_solution = True
    hint_session.touch()

    # Log reveal event
    event_logger = EventLogger()
    event_logger.log_event(db, session_id, "reveal_used", {})

    db.commit()

    return RevealResponse(
        session_id=session_id,
        steps=solution.steps,
        final_answer=solution.final_answer,
        explanation=solution.explanation,
        status="REVEALED",
    ).model_dump()


@router.post(
    "/{session_id}/complete",
    response_model=CompleteResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def complete_session(
    session_id: str,
    request: CompleteRequest | None = Body(default=None),
    db: Session = Depends(get_db),
) -> CompleteResponse:
    from backend.services.email_service import get_email_service
    from backend.services.learning_summary import LearningSummaryGenerator
    import io
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas as pdf_canvas

    # Validate session_id format
    validate_session_id(session_id)

    hint_session = db.query(HintSession).filter(HintSession.id == session_id).first()

    if not hint_session:
        raise HTTPException(
            status_code=404,
            detail={"error": "SESSION_NOT_FOUND", "message": get_message("SESSION_NOT_FOUND")},
        )

    allowed_layers = [HintLayer.STEP, HintLayer.COMPLETED]
    if hint_session.current_layer not in allowed_layers:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "COMPLETE_NOT_ALLOWED",
                "message": get_message("COMPLETE_NOT_ALLOWED"),
            },
        )

    hint_session.status = SessionStatus.COMPLETED
    hint_session.current_layer = HintLayer.COMPLETED
    hint_session.touch()

    if request and request.email:
        hint_session.parent_email = request.email

    # Log completion event
    event_logger = EventLogger()
    event_logger.log_event(db, session_id, "session_completed", {})

    db.commit()

    # Send email report if email provided
    email_sent = False
    if request and request.email:
        try:
            # Generate learning summary
            summary_generator = LearningSummaryGenerator()
            summary = summary_generator.generate_session_summary(db, session_id)

            # Generate PDF report (simplified version)
            buffer = io.BytesIO()
            p = pdf_canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            p.setFont("Helvetica-Bold", 20)
            p.drawString(50, height - 50, "StepWise Session Report")
            p.setFont("Helvetica", 12)
            p.drawString(50, height - 80, f"Session ID: {session_id}")
            p.drawString(50, height - 100, f"Performance: {summary['performance_level']}")

            p.showPage()
            p.save()
            pdf_content = buffer.getvalue()
            buffer.close()

            # Send email
            email_service = get_email_service()
            email_sent = email_service.send_learning_report(
                recipient_email=request.email,
                session_id=session_id,
                summary=summary,
                pdf_content=pdf_content,
            )
        except Exception as e:
            # Log error but don't fail the completion
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send email report: {e}", exc_info=True)
            email_sent = False

    return CompleteResponse(
        session_id=session_id,
        status="COMPLETED",
        message=get_message("COMPLETE_SUCCESS"),
        email_sent=email_sent,
    )


@router.post(
    "/{session_id}/events",
    responses={
        200: {"description": "Event logged successfully"},
        404: {"model": ErrorResponse},
    },
)
async def log_event(
    session_id: str,
    request: dict,
    db: Session = Depends(get_db),
) -> dict:
    """Log a custom event for analytics (frontend fire-and-forget calls)."""
    # Validate session_id format
    validate_session_id(session_id)

    hint_session = db.query(HintSession).filter(HintSession.id == session_id).first()

    if not hint_session:
        raise HTTPException(
            status_code=404,
            detail={"error": "SESSION_NOT_FOUND", "message": get_message("SESSION_NOT_FOUND")},
        )

    event_type = request.get("event_type", "custom_event")
    details = request.get("details")

    event_logger = EventLogger()
    event_logger.log_event(db, session_id, event_type, details)
    db.commit()

    return {"status": "ok", "event_type": event_type}
