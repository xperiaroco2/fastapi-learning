from pydantic import UUID4, Field

from app.schemas.base import BaseRequest, BaseResponse


class StudentResponse(BaseResponse):
    id: UUID4
    first_name: str
    last_name: str
    academic_profile: str


class CreateStudentRequest(BaseRequest):
    first_name: str = Field(
        min_length=4,
        max_length=40,
    )
    last_name: str = Field(
        min_length=4,
        max_length=40,
    )
    academic_profile: str | None = Field(min_length=10, max_length=1000, default=None)
