from pydantic import BaseModel, Field


class StartSessionRequest(BaseModel):
    problem_text: str = Field(...)
    client_id: str | None = Field(default=None)
    locale: str = Field(default="en-US")
    grade_level: int | None = Field(default=None, ge=4, le=9)


class StartSessionResponse(BaseModel):
    session_id: str
    session_access_token: str
    problem_type: str
    topic: str | None = None
    current_layer: str
    hint_content: str
    requires_response: bool = True

    model_config = {"from_attributes": True}


class SessionResponse(BaseModel):
    session_id: str
    problem: dict
    status: str
    current_layer: str
    confusion_count: int
    layers_completed: list[str]
    can_reveal_solution: bool
    last_hint: str | None
    started_at: str
    last_active_at: str

    model_config = {"from_attributes": True}
