"""Error response schemas for API."""

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed error information."""

    field: str | None = Field(default=None, description="Field that caused the error")
    message: str = Field(..., description="Error message for this field")


class ErrorResponse(BaseModel):
    """Standard error response format.

    All API errors should return this structure for consistency.
    """

    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Human-readable error message")
    details: list[ErrorDetail] | None = Field(
        default=None, description="Additional error details for validation errors"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "validation_error",
                    "message": "Invalid input",
                    "details": [{"field": "raw_text", "message": "Problem text is required"}],
                },
                {"error": "not_found", "message": "Session not found", "details": None},
            ]
        }
    }
