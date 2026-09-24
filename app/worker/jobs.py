from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import inject_session
from app.services.analyse import AnalyseService


@inject_session
async def analyse_case_job(ctx, run_id: UUID, user_id: UUID, session: AsyncSession):
    analyse_service = AnalyseService(session)
    await analyse_service.analyse_case_run(run_id, user_id)
