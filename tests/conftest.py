import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from api_app import app, settings
from clients.db_client import DBClient

@pytest.fixture(scope="session")
def db_url():
    return settings.DB_URL

@pytest.fixture(scope="session")
async def db_client(db_url):
    client = DBClient(db_url=db_url)
    yield client
    await client.close()

@pytest.fixture(autouse=True)
async def setup_db(db_client):
    """
    Clears and recreates the database schema before each test function.
    """
    await db_client.clear_db()
    await db_client.create_all()

@pytest.fixture
async def db_session(db_url):
    """
    Provides an AsyncSession for integration tests.
    """
    engine = create_async_engine(db_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()

@pytest.fixture
async def test_client():
    """
    Provides a Litestar AsyncTestClient for functional tests.
    """
    async with AsyncTestClient(app=app) as client:
        yield client
