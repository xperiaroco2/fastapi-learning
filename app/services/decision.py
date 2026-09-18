from typing import Annotated
from uuid import UUID

from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import ConflictError, EntityNotFoundError
from app.models import Decision, DecisionAnalysisRun
from app.models.decision import DecisionStatus
from app.schemas.decision import CreateDecisionRequest
from app.services.queue import QueueService, get_queue_service


def get_decision_service(
    db: Annotated[AsyncSession, Depends(get_db)], queue: Annotated[QueueService, Depends(get_queue_service)]
) -> DecisionService:
    return DecisionService(db, queue)


class DecisionService:
    def __init__(self, db: AsyncSession, queue: QueueService):
        self.db = db
        self.queue = queue

    async def get_all(self, user_id: UUID) -> list[Decision]:
        stmt = select(Decision).where(Decision.user_id == user_id)
        decisions = (await self.db.scalars(stmt)).all()

        return list(decisions)

    async def get_by_id(self, decision_id: UUID, user_id: UUID) -> Decision:
        stmt = select(Decision).where(Decision.id == decision_id, Decision.user_id == user_id)
        decision = await self.db.scalar(stmt)

        if not decision:
            raise EntityNotFoundError(entity_name="Decision", entity_field="id", entity_value=decision_id)

        return decision

    async def create(self, body: CreateDecisionRequest, user_id: UUID) -> Decision:
        ai_provider = get_settings().ai_provider

        decision = Decision(
            situation=body.situation,
            chosen_decision=body.chosen_decision,
            personal_reasoning=body.personal_reasoning,
            user_id=user_id,
        )
        self.db.add(decision)
        await self.db.flush()

        decision_run = DecisionAnalysisRun(provider=ai_provider, decision_id=decision.id)
        self.db.add(decision_run)

        await self.db.commit()

        await self.queue.enqueue_analysis_run(run_id=decision_run.id)

        return decision

    async def rerun(self, decision_id: UUID, user_id: UUID) -> UUID:
        decision = await self.get_by_id(decision_id, user_id)
        stmt = (
            select(DecisionAnalysisRun)
            .where(
                DecisionAnalysisRun.decision_id == decision.id, DecisionAnalysisRun.status == DecisionStatus.PROCESSING
            )
            .limit(1)
        )
        processing_run = await self.db.scalar(stmt)

        if processing_run:
            raise ConflictError(
                "Analysis already in progress. Please wait for the current analysis to complete before retrying."
            )

        ai_provider = get_settings().ai_provider
        decision_run = DecisionAnalysisRun(provider=ai_provider, decision_id=decision.id)
        self.db.add(decision_run)

        decision.status = DecisionStatus.PENDING

        await self.db.commit()

        await self.queue.enqueue_analysis_run(run_id=decision_run.id)

        return decision_run.id
