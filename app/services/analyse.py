from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.ai.factory import get_ai_provider
from app.core.constants import CaseStatus
from app.core.exceptions import AnalyseFailedError
from app.core.logger import logger
from app.models import Case
from app.models.run import AnalysisRun


class AnalyseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_provider = get_ai_provider()

    async def analyse_case_run(self, run_id: UUID, user_id: UUID):
        stmt = (
            select(AnalysisRun)
            .where(AnalysisRun.id == run_id)
            .options(joinedload(AnalysisRun.case).joinedload(Case.student))
        )
        run: AnalysisRun | None = await self.db.scalar(stmt)

        if not run or not run.case or not run.case.student:
            raise AnalyseFailedError("invalid_run")

        run.status = CaseStatus.PROCESSING
        run.case.status = CaseStatus.PROCESSING

        await self.db.commit()
        await self.db.refresh(run)

        try:
            result = await self.ai_provider.analyse_case(
                description=run.case.description,
                academic_profile=run.case.student.academic_profile or "",
                run_id=run_id,
                user_id=user_id,
            )
        except AnalyseFailedError as exc:
            run.status = CaseStatus.FAILED
            run.case.status = CaseStatus.FAILED
            run.finished_at = datetime.now()
            run.error = exc.message
            await self.db.commit()
            logger.exception("analysis_failed", run_id=run_id, reason=exc.message)
            return

        run.status = CaseStatus.COMPLETED
        run.case.status = CaseStatus.COMPLETED
        run.hypothesis = result.hypothesis
        run.action_plan = result.action_plan
        run.grounded = result.grounded
        run.finished_at = datetime.now()

        await self.db.commit()

        logger.info("analysis_success")
