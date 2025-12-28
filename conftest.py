import pytest
import asyncpg
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import app, settings
from clients.db_client import DBClient
from orm.models.user import User
from sqlalchemy import select
from pgqueuer.queries import Queries


@pytest.fixture(scope="session")
def db_url():
    return settings.db_url


@pytest.fixture(scope="session")
async def db_client(db_url):
    client = DBClient(db_url=db_url)
    yield client
    await client.close()


@pytest.fixture(autouse=True)
async def setup_db(db_client: DBClient):
    """
    Clears and recreates the database schema before each test function.
    Also seeds a default admin user.
    """
    await db_client.clear_db()
    await db_client.create_all()

    # Apply pgqueuer schema to broker db
    broker_url = settings.broker_url.replace("+asyncpg", "")
    conn = await asyncpg.connect(broker_url)
    q = Queries.from_asyncpg_connection(conn)
    
    try:
        await q.install()
    except asyncpg.exceptions.DuplicateObjectError:
        pass

    await db_client.seed_db()  # Seed the admin user here

    yield

    # Teardown
    await q.uninstall()
    await conn.close()


@pytest.fixture
async def admin_user_id(
    db_client: DBClient, setup_db
):  # Depend on setup_db to ensure it runs
    # Query for the admin user seeded in setup_db
    # This requires a session. We'll reuse the db_client's engine and create a temporary session.
    async_session = async_sessionmaker(db_client.engine, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.email == "admin@museum.com")
        )
        admin_user = result.scalars().first()
        assert admin_user is not None
        return str(admin_user.id)


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


@pytest.fixture
async def authenticated_test_client(test_client: AsyncTestClient, admin_user_id: str):
    """
    Provides a Litestar AsyncTestClient with X-User-ID header set.
    """
    test_client.headers["X-User-ID"] = admin_user_id
    return test_client
