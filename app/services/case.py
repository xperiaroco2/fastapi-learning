from typing import Annotated
from uuid import UUID

from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.constants import CaseStatus
from app.core.database import get_db
from app.core.exceptions import ConflictError, EntityNotFoundError
from app.models.case import Case
from app.models.run import AnalysisRun
from app.schemas.case import CreateCaseRequest
from app.services.queue import QueueService, get_queue_service


def get_case_service(
    db: Annotated[AsyncSession, Depends(get_db)], queue: Annotated[QueueService, Depends(get_queue_service)]
) -> CaseService:
    return CaseService(db, queue)


class CaseService:
    def __init__(self, db: AsyncSession, queue: QueueService):
        self.db = db
        self.queue = queue

    async def get_all(self, user_id: UUID) -> list[Case]:
        stmt = select(Case).where(Case.teacher_id == user_id)
        cases = (await self.db.scalars(stmt)).all()

        return list(cases)

    async def get_by_id(self, case_id: UUID, user_id: UUID) -> Case:
        stmt = select(Case).where(Case.id == case_id, Case.teacher_id == user_id)
        case = await self.db.scalar(stmt)

        if not case:
            raise EntityNotFoundError(entity_name="Case", entity_field="id", entity_value=case_id)

        return case

    async def create(self, body: CreateCaseRequest, user_id: UUID) -> Case:
        ai_provider = get_settings().ai_provider

        case = Case(
            description=body.description,
            teacher_id=user_id,
            student_id=body.student_id,
        )
        self.db.add(case)
        await self.db.flush()

        case_run = AnalysisRun(provider=ai_provider, case_id=case.id)
        self.db.add(case_run)

        await self.db.commit()

        await self.queue.enqueue_analyze_case(run_id=case_run.id)

        return case

    async def rerun(self, case_id: UUID, user_id: UUID) -> UUID:
        case = await self.get_by_id(case_id, user_id)
        stmt = (
            select(AnalysisRun)
            .where(AnalysisRun.case_id == case.id, AnalysisRun.status == CaseStatus.PROCESSING)
            .limit(1)
        )
        processing_run = await self.db.scalar(stmt)

        if processing_run:
            raise ConflictError(
                "Analysis already in progress. Please wait for the current analysis to complete before retrying."
            )

        ai_provider = get_settings().ai_provider
        case_run = AnalysisRun(provider=ai_provider, case_id=case.id)
        self.db.add(case_run)

        case.status = CaseStatus.PENDING

        await self.db.commit()

        await self.queue.enqueue_analyze_case(run_id=case_run.id)

        return case_run.id
