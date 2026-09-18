from asyncio import sleep
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.database import inject_session
from app.core.exceptions import EntityNotFoundError
from app.models import DecisionAnalysisRun
from app.models.decision import DecisionStatus


# todo: move to analysis service
@inject_session
async def decision_analysis_job(ctx, run_id: UUID, session: AsyncSession):
    stmt = (
        select(DecisionAnalysisRun)
        .where(DecisionAnalysisRun.id == run_id)
        .options(joinedload(DecisionAnalysisRun.decision))
    )
    run: DecisionAnalysisRun | None = await session.scalar(stmt)

    if not run:
        raise EntityNotFoundError(entity_name="Run", entity_field="id", entity_value=run_id)

    run.status = DecisionStatus.PROCESSING
    run.decision.status = DecisionStatus.PROCESSING

    await session.commit()

    # start AI processing
    await sleep(10)

    await session.refresh(run)

    run.status = DecisionStatus.COMPLETED
    run.decision.status = DecisionStatus.COMPLETED
    run.category_text = "test situation"
    run.biases_text = ["test biases_text"]
    run.finished_at = datetime.now()
    run.result_json = {
        "category": "test category",
        "cognitive_biases": "test cognitive_biases",
        "missed_alternatives": "test missed_alternatives",
        "insights": "test insights",
        "raw_ai_response": "test raw_ai_response",
    }

    await session.commit()
