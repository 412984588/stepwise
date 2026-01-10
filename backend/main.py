"""FastAPI application entry point for StepWise backend."""

import logging
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from typing import Any

import sentry_sdk
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api import api_router
from backend.database.engine import init_db
from backend.middleware import BetaAccessMiddleware

SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        send_default_pii=False,
    )

# Configure logging
logger = logging.getLogger(__name__)

# Configure logging
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    Runs on startup and shutdown.
    """
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: Cleanup if needed


# Create FastAPI application
app = FastAPI(
    title="StepWise API",
    description="Socratic-style math tutoring system with layered hints",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
# In production, replace with specific origins
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:3000,http://127.0.0.1:3001",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(BetaAccessMiddleware)

# Include API router
app.include_router(api_router)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Flatten HTTPException detail for consistent error response format.

    Converts {"detail": {"error": "...", "message": "..."}}
    to {"error": "...", "message": "..."}

    Also preserves any headers from the HTTPException (e.g., Retry-After for 429 responses).
    """
    content: dict[str, Any]
    if isinstance(exc.detail, dict):
        content = exc.detail
    else:
        content = {"error": "ERROR", "message": str(exc.detail)}
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers if exc.headers else None,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler to prevent stack traces from leaking to clients.

    Logs the full error server-side but returns a safe generic message to clients.
    """
    # Log the full error server-side
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method},
    )

    # Return safe error to client (no stack trace)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An internal error occurred. Please try again later.",
        },
    )


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": "StepWise API",
        "version": "0.1.0",
        "docs": "/docs",
    }
