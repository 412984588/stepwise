"""FastAPI dependencies for security and access control."""

import logging
import os
from typing import Optional

from fastapi import Header, HTTPException, Request, Depends, status
from sqlalchemy.orm import Session

from backend.database.engine import get_db
from backend.models.session import HintSession
from backend.services.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


def verify_beta_code(x_beta_code: str | None = Header(None, alias="X-Beta-Code")) -> str | None:
    """
    Verify beta access code from request header.

    If BETA_ACCESS_CODE env var is not set, gate is disabled (dev-friendly).
    If set, the X-Beta-Code header must match.

    Args:
        x_beta_code: Beta code from X-Beta-Code header

    Returns:
        The verified beta code, or None if gate is disabled

    Raises:
        HTTPException: 403 if gate is enabled and code is missing/invalid
    """
    expected_code = os.getenv("BETA_ACCESS_CODE")

    # If no beta code is configured, gate is disabled
    if not expected_code:
        return None

    # Gate is enabled - code must be provided and match
    if not x_beta_code:
        logger.warning("Beta access denied: missing X-Beta-Code header")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "BETA_CODE_REQUIRED",
                "message": "Private beta access code is required. Please enter your beta code.",
            },
        )

    if x_beta_code != expected_code:
        logger.warning(f"Beta access denied: invalid code (got {x_beta_code[:4]}...)")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "BETA_CODE_INVALID",
                "message": "Invalid beta access code. Please check your code and try again.",
            },
        )

    logger.info("Beta access granted")
    return x_beta_code


def verify_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")) -> str:
    """
    Verify API access key from request header.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        The verified API key

    Raises:
        HTTPException: 401 if key is missing or invalid
    """
    expected_key = os.getenv("API_ACCESS_KEY")

    # If no API key is configured in environment, allow access
    # (for development/testing environments without security)
    if not expected_key:
        return ""

    # If API key is configured, it must be provided and match
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "API_KEY_MISSING",
                "message": "API access key is required. Please provide X-API-Key header.",
            },
        )

    if x_api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "API_KEY_INVALID",
                "message": "Invalid API access key.",
            },
        )

    return x_api_key


def check_rate_limit(rate_limiter: RateLimiter):
    """
    Create a dependency that checks rate limits for a client.

    Args:
        rate_limiter: RateLimiter instance to use

    Returns:
        Dependency function that checks rate limits
    """

    def _check_rate_limit(request: Request) -> None:
        """
        Check if client has exceeded rate limit.

        Args:
            request: FastAPI request object

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        # Use client IP as identifier
        client_id = request.client.host if request.client else "unknown"

        if not rate_limiter.is_allowed(client_id):
            retry_after = rate_limiter.get_retry_after(client_id)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": f"Too many requests. Please try again in {retry_after} seconds.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

    return _check_rate_limit


def verify_session_access(
    session_id: str,
    x_session_access_token: Optional[str] = Header(None, alias="X-Session-Access-Token"),
    db: Session = Depends(get_db),
) -> HintSession:
    """
    Verify session access token matches session.

    This dependency protects endpoints that should only be accessed
    by the session owner. The browser sends the token it received
    from session start in the X-Session-Access-Token header.

    Args:
        session_id: Session UUID from path parameter
        x_session_access_token: Token from request header
        db: Database session

    Returns:
        HintSession object if token valid

    Raises:
        HTTPException: 403 if token missing/invalid, 404 if session not found
    """
    if not x_session_access_token:
        logger.warning(f"Session access denied: missing token for {session_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "MISSING_SESSION_TOKEN",
                "message": "X-Session-Access-Token header required",
            },
        )

    session = db.query(HintSession).filter(HintSession.id == session_id).first()
    if not session:
        logger.warning(f"Session access denied: session {session_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "SESSION_NOT_FOUND", "message": "Session not found"},
        )

    if session.session_access_token != x_session_access_token:
        logger.warning(
            f"Session access denied: invalid token for {session_id} "
            f"(expected {session.session_access_token[:8] if session.session_access_token else 'None'}..., "
            f"got {x_session_access_token[:8]}...)"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "INVALID_SESSION_TOKEN",
                "message": "Invalid session access token",
            },
        )

    logger.info(f"Session access granted: {session_id}")
    return session
