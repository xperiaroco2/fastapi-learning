from collections.abc import AsyncGenerator

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core import get_settings

DATABASE_URL = get_settings().database_url

engine = create_async_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def check_db_connection():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful!")
    except Exception as e:
        logger.error("Database connection failed!")
        raise e


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as db_session:
        yield db_session
