from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.logger import logger

DATABASE_URL = get_settings().database_url
SQL_ECHO = get_settings().sql_echo

engine = create_async_engine(DATABASE_URL, echo=SQL_ECHO, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def check_db_connection():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("db_connection_success")
    except Exception as e:
        logger.error("db_connection_error")
        raise e


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as db_session:
        yield db_session
