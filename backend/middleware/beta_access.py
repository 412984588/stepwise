import logging
import os
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

EXCLUDED_PATHS = frozenset(
    {
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/favicon.ico",
    }
)

EXCLUDED_PREFIXES = (
    "/docs/",
    "/redoc/",
    "/api/v1/health",
    "/api/v1/email/unsubscribe",
    "/api/v1/email/preferences",
    "/api/v1/feedback",
)


class BetaAccessMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, beta_code: str | None = None) -> None:
        super().__init__(app)
        self._static_beta_code = beta_code

    def _get_beta_code(self) -> str | None:
        if self._static_beta_code is not None:
            return self._static_beta_code
        return os.getenv("BETA_ACCESS_CODE")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        beta_code = self._get_beta_code()
        if not beta_code:
            return await call_next(request)

        path = request.url.path

        if self._is_excluded_path(path):
            return await call_next(request)

        x_beta_code = request.headers.get("X-Beta-Code")

        if not x_beta_code:
            logger.warning(f"Beta access denied: missing X-Beta-Code header for {path}")
            return JSONResponse(
                status_code=403,
                content={
                    "error": "BETA_CODE_REQUIRED",
                    "message": "Private beta access code is required. Please enter your beta code.",
                },
            )

        if x_beta_code != beta_code:
            logger.warning(f"Beta access denied: invalid code for {path}")
            return JSONResponse(
                status_code=403,
                content={
                    "error": "BETA_CODE_INVALID",
                    "message": "Invalid beta access code. Please check your code and try again.",
                },
            )

        logger.debug(f"Beta access granted for {path}")
        return await call_next(request)

    def _is_excluded_path(self, path: str) -> bool:
        if path in EXCLUDED_PATHS:
            return True
        for prefix in EXCLUDED_PREFIXES:
            if path.startswith(prefix):
                return True
        return False
