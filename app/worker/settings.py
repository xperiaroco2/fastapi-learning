from app.core.config import get_settings
from app.worker.jobs import decision_analysis_job
from arq.connections import RedisSettings


class WorkerSettings:
    functions = [decision_analysis_job]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    keep_result = 60 * 60  # 1 hour
    max_jobs = 20
