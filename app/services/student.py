from typing import Annotated
from uuid import UUID

from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import EntityNotFoundError
from app.models.student import Student
from app.schemas.student import CreateStudentRequest


def get_student_service(db: Annotated[AsyncSession, Depends(get_db)]) -> StudentService:
    return StudentService(db)


class StudentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Student]:
        stmt = select(Student)
        students = (await self.db.scalars(stmt)).all()

        return list(students)

    async def get_by_id(self, student_id: UUID) -> Student:
        stmt = select(Student).where(Student.id == student_id)
        student = await self.db.scalar(stmt)

        if not student:
            raise EntityNotFoundError(entity_name="Student", entity_field="id", entity_value=student_id)

        return student

    async def create(self, body: CreateStudentRequest) -> Student:
        student = Student(
            first_name=body.first_name,
            last_name=body.last_name,
            academic_profile=body.academic_profile,
        )
        self.db.add(student)

        await self.db.commit()
        await self.db.refresh(student)

        return student
