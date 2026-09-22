from datetime import datetime
from uuid import UUID

from anyio import sleep
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.constants import CaseStatus
from app.core.exceptions import AnalyseFailedError
from app.models.run import AnalysisRun


class AnalyseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyse_case_run(self, run_id: UUID):
        stmt = select(AnalysisRun).where(AnalysisRun.id == run_id).options(joinedload(AnalysisRun.case))
        run: AnalysisRun | None = await self.db.scalar(stmt)

        if not run:
            raise AnalyseFailedError()

        run.status = CaseStatus.PROCESSING
        run.case.status = CaseStatus.PROCESSING

        await self.db.commit()

        # start AI processing
        await sleep(10)

        await self.db.refresh(run)

        run.status = CaseStatus.COMPLETED
        run.case.status = CaseStatus.COMPLETED
        run.hypothesis = "test hypothesis"
        run.action_plan = {"0": "test first step", "1": "test second step"}
        run.finished_at = datetime.now()

        await self.db.commit()
