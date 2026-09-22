from arq import func
from arq.connections import RedisSettings

from app.core.config import get_settings
from app.core.constants import TaskNames
from app.worker.jobs import analyse_case_job


class WorkerSettings:
    functions = [
        func(analyse_case_job, name=TaskNames.ANALYSE_CASE)  # type: ignore
    ]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    keep_result = 60 * 60  # 1 hour
    max_jobs = 20
