from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, status
from fastapi.params import Depends

from app.core.dependencies import get_current_user
from app.schemas.student import CreateStudentRequest, StudentResponse
from app.services.student import StudentService, get_student_service

student_router = APIRouter(prefix="/students", tags=["Student"], dependencies=[Depends(get_current_user)])


@student_router.get("", response_model=list[StudentResponse])
async def get_students(
    student_service: Annotated[StudentService, Depends(get_student_service)],
) -> list[StudentResponse]:
    students = await student_service.get_all()

    return [StudentResponse.model_validate(student) for student in students]


@student_router.get("/{student_id}", response_model=StudentResponse)
async def get_student_by_id(
    student_service: Annotated[StudentService, Depends(get_student_service)],
    student_id: UUID,
) -> StudentResponse:
    student = await student_service.get_by_id(student_id)

    return StudentResponse.model_validate(student)


@student_router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_service: Annotated[StudentService, Depends(get_student_service)],
    body: CreateStudentRequest,
) -> StudentResponse:
    student = await student_service.create(body)

    return StudentResponse.model_validate(student)
