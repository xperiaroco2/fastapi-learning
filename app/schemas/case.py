from uuid import UUID

from pydantic import UUID4, Field

from app.core.constants import CaseStatus
from app.schemas.base import BaseRequest, BaseResponse


class CaseResponse(BaseResponse):
    id: UUID4
    description: str
    teacher_id: UUID
    student_id: UUID
    status: CaseStatus


class RerunCaseResponse(BaseResponse):
    message: str
    run_id: UUID


class CreateCaseRequest(BaseRequest):
    description: str = Field(
        min_length=20,
        max_length=1000,
    )
    student_id: UUID
