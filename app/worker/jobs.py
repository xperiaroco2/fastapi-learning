from app.core.database import inject_session
from sqlalchemy.ext.asyncio import AsyncSession


@inject_session
async def decision_analysis_job(ctx, session: AsyncSession = None):
    pass
