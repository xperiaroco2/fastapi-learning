import asyncio
from contextlib import asynccontextmanager
from typing import Annotated

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from starlette.types import Lifespan

from app.core.config import get_settings
from app.core.database import check_db_connection, engine, run_migrations
from app.core.exception_handlers import setup_exception_handlers
from app.core.logger import logger, setup_logging
from app.core.middlewares import LoggingMiddleware
from app.core.redis_client import close_redis, connect_redis, get_redis
from app.routes.auth import auth_router
from app.routes.case import case_router


@asynccontextmanager
async def app_init(app: FastAPI):
    await check_db_connection()
    await connect_redis()
    await asyncio.to_thread(run_migrations)
    app.state.arq_pool = await create_pool(RedisSettings.from_dsn(get_settings().redis_url))
    logger.info("server_started")
    yield
    await engine.dispose()
    await app.state.arq_pool.close()
    await close_redis()
    logger.info("server_stopped")


setup_logging()


def create_app(lifespan: Lifespan | None = app_init) -> FastAPI:
    new_app = FastAPI(lifespan=lifespan)

    origins = ["http://localhost:3000"]

    new_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    new_app.add_middleware(LoggingMiddleware)

    new_app.include_router(auth_router)
    new_app.include_router(case_router)

    setup_exception_handlers(new_app)

    @new_app.get("/health")
    async def health_check():
        logger.info("health_check")
        return {"status": "ok"}

    @new_app.get("/health/redis")
    async def redis_health(r: Annotated[Redis, Depends(get_redis)]):
        pong = await r.ping()
        return {"redis": pong}

    return new_app


app = create_app()
