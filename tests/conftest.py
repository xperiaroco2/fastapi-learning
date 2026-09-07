import pytest
from alembic import command
from alembic.config import Config
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.database import get_db
from app.main import create_app
from app.models.base import Base

TEST_DATABASE_URL = get_settings().test_database_url
test_app = create_app(lifespan=None)


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(cfg, "head")


@pytest.fixture
async def db_session():
    test_engine = create_async_engine(TEST_DATABASE_URL)
    testing_session = async_sessionmaker(bind=test_engine, class_=AsyncSession)

    async with testing_session() as session:
        yield session
        table_names = ", ".join(Base.metadata.tables.keys())
        await session.execute(text(f"TRUNCATE {table_names} CASCADE"))
        await session.commit()

    await test_engine.dispose()


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    test_app.dependency_overrides.clear()
