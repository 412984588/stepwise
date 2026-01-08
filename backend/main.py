"""FastAPI application entry point for StepWise backend."""

import os
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api import api_router
from backend.database.engine import init_db


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
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(
    ","
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Flatten HTTPException detail for consistent error response format.

    Converts {"detail": {"error": "...", "message": "..."}}
    to {"error": "...", "message": "..."}
    """
    content: dict[str, Any]
    if isinstance(exc.detail, dict):
        content = exc.detail
    else:
        content = {"error": "ERROR", "message": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content=content)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": "StepWise API",
        "version": "0.1.0",
        "docs": "/docs",
    }
