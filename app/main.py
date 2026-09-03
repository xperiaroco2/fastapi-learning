from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import check_db_connection, engine
from app.core.exception_handlers import setup_exception_handlers
from app.core.logger import logger, setup_logging
from app.core.middlewares import LoggingMiddleware
from app.routes.auth import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_db_connection()
    logger.info("server_started")
    yield
    logger.info("server_stopped")
    await engine.dispose()


setup_logging()

app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.include_router(auth_router)

setup_exception_handlers(app)


@app.get("/health")
async def health_check():
    logger.info("health_check")
    return {"status": "ok"}
