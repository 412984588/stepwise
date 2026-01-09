"""API router module for StepWise backend."""

from fastapi import APIRouter

# Main API router - all endpoint routers will be included here
api_router = APIRouter(prefix="/api/v1")


@api_router.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


from backend.api.sessions import router as sessions_router
from backend.api.stats import router as stats_router
from backend.api.billing import router as billing_router
from backend.api.reports import router as reports_router
from backend.api.email import router as email_router
from backend.api.feedback import router as feedback_router

api_router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
api_router.include_router(stats_router)
api_router.include_router(billing_router, prefix="/billing", tags=["billing"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(email_router)
api_router.include_router(feedback_router)
