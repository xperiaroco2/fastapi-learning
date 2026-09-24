from arq import func
from arq.connections import RedisSettings
from phoenix.otel import register

from app.core.config import get_settings
from app.core.constants import TaskNames
from app.core.logger import setup_logging
from app.worker.jobs import analyse_case_job

setup_logging()

register(project_name="my-llm-app", auto_instrument=True)


class WorkerSettings:
    functions = [
        func(analyse_case_job, name=TaskNames.ANALYSE_CASE)  # type: ignore
    ]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    keep_result = 60 * 60  # 1 hour
    max_jobs = 20
