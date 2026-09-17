from arq.connections import RedisSettings


async def startup(ctx):
    pass


async def shutdown(ctx):
    pass


class WorkerSettings:
    functions = []
    redis_settings = RedisSettings()
    keep_result = 60 * 60  # 1 hour
    max_jobs = 20
    on_startup = startup
    on_shutdown = shutdown
