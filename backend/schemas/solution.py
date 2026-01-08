from pydantic import BaseModel, Field


class SolutionStep(BaseModel):
    description: str
    result: str


class RevealResponse(BaseModel):
    session_id: str
    steps: list[dict[str, str]]
    final_answer: str
    explanation: str | None = None
    status: str = "REVEALED"

    model_config = {"from_attributes": True}


class CompleteResponse(BaseModel):
    session_id: str
    status: str = "COMPLETED"
    message: str = "恭喜你独立完成了这道题！"

    model_config = {"from_attributes": True}
