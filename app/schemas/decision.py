from uuid import UUID

from pydantic import UUID4, Field

from app.schemas.base import BaseRequest, BaseResponse


class DecisionResponse(BaseResponse):
    id: UUID4
    situation: str
    chosen_decision: str
    personal_reasoning: str | None


class RerunDecisionResponse(BaseResponse):
    message: str
    run_id: UUID


class CreateDecisionRequest(BaseRequest):
    situation: str = Field(
        min_length=20,
        max_length=1000,
    )
    chosen_decision: str = Field(min_length=10, max_length=1000)
    personal_reasoning: str | None = Field(min_length=10, max_length=1000, default=None)
