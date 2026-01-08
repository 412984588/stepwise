"""API endpoints for learning statistics and session history."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.stats import StatsSummary, SessionListResponse, DashboardResponse
from backend.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummary)
def get_stats_summary(db: Session = Depends(get_db)) -> StatsSummary:
    service = StatsService(db)
    return service.get_summary()


@router.get("/sessions", response_model=SessionListResponse)
def list_sessions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> SessionListResponse:
    service = StatsService(db)
    sessions = service.list_sessions(limit=limit, offset=offset)
    total = service.count_sessions()

    return SessionListResponse(
        sessions=sessions,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)) -> DashboardResponse:
    service = StatsService(db)
    return service.get_dashboard()
