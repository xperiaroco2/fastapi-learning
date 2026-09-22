from typing import Annotated
from uuid import UUID

from arq import ArqRedis
from fastapi.params import Depends

from app.core.arq import get_arq_pool
from app.core.constants import TaskNames


def get_queue_service(arq: Annotated[ArqRedis, Depends(get_arq_pool)]) -> QueueService:
    return QueueService(arq)


class QueueService:
    def __init__(self, arq: ArqRedis):
        self.arq = arq

    async def enqueue_analyze_case(self, run_id: UUID):
        await self.arq.enqueue_job(TaskNames.ANALYSE_CASE, run_id, _job_id=f"{TaskNames.ANALYSE_CASE}_{run_id}")
