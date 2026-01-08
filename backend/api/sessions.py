import re
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
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
from backend.schemas.errors import ErrorResponse
from backend.services.problem_classifier import ProblemClassifier
from backend.services.hint_generator import HintGenerator
from backend.services.understanding_evaluator import UnderstandingEvaluator
from backend.services.session_manager import SessionManager

MIN_RESPONSE_LENGTH = 10

router = APIRouter()


def generate_session_id() -> str:
    return f"ses_{uuid.uuid4().hex[:8]}"


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
        422: {"model": ErrorResponse},
    },
)
async def start_session(
    request: StartSessionRequest,
    db: Session = Depends(get_db),
) -> StartSessionResponse:
    problem_text = request.problem_text.strip()

    if not problem_text:
        raise HTTPException(
            status_code=400,
            detail={"error": "EMPTY_INPUT", "message": "请输入一道数学题"},
        )

    if len(problem_text) > 500:
        raise HTTPException(
            status_code=400,
            detail={"error": "TOO_LONG", "message": "题目太长了，请精简后重试"},
        )

    if not is_math_problem(problem_text):
        raise HTTPException(
            status_code=400,
            detail={"error": "NOT_MATH", "message": "这看起来不是数学题，请输入一道数学题试试"},
        )

    classifier = ProblemClassifier()
    problem_type = classifier.classify(problem_text)

    problem = Problem(
        raw_text=problem_text,
        problem_type=problem_type,
    )
    db.add(problem)
    db.flush()

    session_id = generate_session_id()
    hint_session = HintSession(
        id=session_id,
        problem_id=problem.id,
        current_layer=HintLayer.CONCEPT,
        status=SessionStatus.ACTIVE,
    )
    db.add(hint_session)
    db.flush()

    generator = HintGenerator()
    hint = generator.generate(
        problem_text=problem_text,
        problem_type=problem_type,
        layer=HintLayer.CONCEPT,
    )

    hint_content = HintContent(
        session_id=session_id,
        layer=HintLayer.CONCEPT,
        sequence=1,
        content=hint.content,
        is_downgrade=False,
    )
    db.add(hint_content)
    db.commit()

    return StartSessionResponse(
        session_id=session_id,
        problem_type=problem_type.value.upper(),
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
    hint_session = db.query(HintSession).filter(HintSession.id == session_id).first()

    if not hint_session:
        raise HTTPException(
            status_code=404,
            detail={"error": "SESSION_NOT_FOUND", "message": "会话不存在"},
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
        404: {"model": ErrorResponse},
    },
)
async def respond_to_hint(
    session_id: str,
    request: RespondRequest,
    db: Session = Depends(get_db),
) -> RespondResponse:
    hint_session = db.query(HintSession).filter(HintSession.id == session_id).first()

    if not hint_session:
        raise HTTPException(
            status_code=404,
            detail={"error": "SESSION_NOT_FOUND", "message": "会话不存在"},
        )

    if hint_session.status != SessionStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail={"error": "SESSION_COMPLETED", "message": "会话已结束"},
        )

    response_text = request.response_text.strip()

    if len(response_text) < MIN_RESPONSE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail={"error": "RESPONSE_TOO_SHORT", "message": "能再多写一点你的想法吗？"},
        )

    problem = db.query(Problem).filter(Problem.id == hint_session.problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=404,
            detail={"error": "PROBLEM_NOT_FOUND", "message": "题目不存在"},
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

    hint_session = db.query(HintSession).filter(HintSession.id == session_id).first()

    if not hint_session:
        raise HTTPException(
            status_code=404,
            detail={"error": "SESSION_NOT_FOUND", "message": "会话不存在"},
        )

    session_manager = SessionManager()
    if not session_manager.can_reveal_solution(hint_session.current_layer, hint_session.status):
        raise HTTPException(
            status_code=400,
            detail={"error": "REVEAL_NOT_ALLOWED", "message": "请先完成所有提示层级"},
        )

    problem = db.query(Problem).filter(Problem.id == hint_session.problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=404,
            detail={"error": "PROBLEM_NOT_FOUND", "message": "题目不存在"},
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
    responses={
        200: {"description": "Session completed successfully"},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def complete_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> dict:
    from backend.schemas.solution import CompleteResponse

    hint_session = db.query(HintSession).filter(HintSession.id == session_id).first()

    if not hint_session:
        raise HTTPException(
            status_code=404,
            detail={"error": "SESSION_NOT_FOUND", "message": "会话不存在"},
        )

    allowed_layers = [HintLayer.STEP, HintLayer.COMPLETED]
    if hint_session.current_layer not in allowed_layers:
        raise HTTPException(
            status_code=400,
            detail={"error": "COMPLETE_NOT_ALLOWED", "message": "请先完成更多提示"},
        )

    hint_session.status = SessionStatus.COMPLETED
    hint_session.current_layer = HintLayer.COMPLETED
    hint_session.touch()
    db.commit()

    return CompleteResponse(
        session_id=session_id,
        status="COMPLETED",
        message="恭喜你独立完成了这道题！",
    ).model_dump()
