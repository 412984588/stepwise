"""Validation utilities for security hardening."""

import re
import uuid
from typing import Optional, Tuple

from fastapi import HTTPException, status


UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.IGNORECASE
)

# RFC 5322 compliant email regex (simplified)
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def is_valid_uuid_v4(value: str) -> bool:
    """
    Validate if a string is a valid UUID v4 format.

    Args:
        value: String to validate

    Returns:
        True if valid UUID v4, False otherwise
    """
    if not value or not isinstance(value, str):
        return False
    return bool(UUID_PATTERN.match(value))


def validate_session_id(session_id: str) -> str:
    """
    Validate session_id format and raise HTTPException if invalid.

    Args:
        session_id: Session ID to validate

    Returns:
        The validated session_id

    Raises:
        HTTPException: 404 if session_id format is invalid
    """
    if not is_valid_uuid_v4(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "SESSION_NOT_FOUND",
                "message": "Session not found. Please check your session ID.",
            },
        )
    return session_id


def generate_session_id() -> str:
    """
    Generate a cryptographically secure UUID v4 session ID.

    Returns:
        UUID v4 string
    """
    return str(uuid.uuid4())


def validate_email_format(email: str) -> bool:
    """
    Validate email address format (RFC 5322 simplified).

    Args:
        email: Email address to validate

    Returns:
        True if valid format, False otherwise
    """
    if not email:
        return False

    if len(email) > 255:
        return False

    if email.count("@") != 1:
        return False

    if not EMAIL_REGEX.match(email):
        return False

    local, domain = email.split("@")
    if len(local) > 64 or len(domain) > 255:
        return False

    if "." not in domain:
        return False

    return True


def validate_email_with_error(email: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate email and return detailed error message.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not email:
        return False, "Email address is required"

    if len(email) > 255:
        return False, "Email address too long (max 255 characters)"

    if email.count("@") != 1:
        return False, "Email must contain exactly one @ symbol"

    if not EMAIL_REGEX.match(email):
        return False, "Invalid email format"

    local, domain = email.split("@")

    if len(local) > 64:
        return False, "Local part of email too long (max 64 characters)"

    if len(domain) > 255:
        return False, "Domain part of email too long (max 255 characters)"

    if "." not in domain:
        return False, "Domain must contain at least one dot"

    return True, None
