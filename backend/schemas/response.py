from pydantic import BaseModel, Field, field_validator


class RespondRequest(BaseModel):
    response_text: str = Field(..., min_length=1)

    @field_validator("response_text")
    @classmethod
    def validate_not_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Response text cannot be empty")
        return v.strip()


class RespondResponse(BaseModel):
    session_id: str
    current_layer: str
    previous_layer: str | None = None
    understanding_level: str
    confusion_count: int | None = None
    is_downgrade: bool = False
    hint_content: str
    requires_response: bool = True
    can_reveal_solution: bool = False

    model_config = {"from_attributes": True}
