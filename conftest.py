import pytest
import asyncpg
from uuid import uuid4
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import text

from app import app, settings
from clients.db_client import DBClient
from orm.models.user import User
from sqlalchemy import select
from pgqueuer.queries import Queries


@pytest.fixture(scope="session")
def postgres_url():
    """
    URL for the default postgres database, used to create/drop test databases.
    """
    # Replace database name in settings.db_url with 'postgres'
    base_url = settings.db_url.rsplit("/", 1)[0]
    return f"{base_url}/postgres"


@pytest.fixture(scope="function")
async def db_name():
    return f"test_db_{uuid4().hex}"


@pytest.fixture(scope="function")
async def db_url(postgres_url, db_name):
    """
    Creates a new database for each test and yields its URL.
    Drops the database after the test.
    """
    engine = create_async_engine(postgres_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        await conn.execute(text(f'CREATE DATABASE "{db_name}"'))

    test_db_url = settings.db_url.rsplit("/", 1)[0] + f"/{db_name}"
    
    yield test_db_url

    async with engine.connect() as conn:
        # Terminate active connections to the test database before dropping
        await conn.execute(
            text(
                f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                AND pid <> pg_backend_pid()
                """
            )
        )
        await conn.execute(text(f'DROP DATABASE "{db_name}"'))
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_client(db_url):
    client = DBClient(db_url=db_url)
    yield client
    await client.close()


@pytest.fixture(autouse=True)
async def setup_db(db_client: DBClient):
    """
    Creates the database schema for the isolated test database.
    """
    await db_client.create_all()

    # Apply pgqueuer schema to broker db (if needed, but usually strictly per-db for app tests)
    # Note: If pgqueuer uses a separate DB, this might need adjustment. 
    # Assuming for now we want it in the test DB or we are mocking it.
    # But looking at settings, broker_url points to a different DB name typically.
    # However, if we want full isolation, we might want to consider how queues are handled.
    # For now, let's keep the existing logic but be aware it might share the broker DB.
    
    broker_url = settings.broker_url.replace("+asyncpg", "")
    conn = await asyncpg.connect(broker_url)
    q = Queries.from_asyncpg_connection(conn)

    try:
        await q.install()
    except asyncpg.exceptions.DuplicateObjectError:
        pass
    
    yield

    # Teardown
    await q.uninstall()
    await conn.close()


@pytest.fixture
async def seed_admin_user(db_client: DBClient):
    """
    Seeds the database with an admin user. 
    Explicitly requested by functional tests.
    """
    await db_client.seed_db()


@pytest.fixture
async def admin_user_id(
    db_client: DBClient, seed_admin_user
): 
    # Query for the admin user seeded
    async_session = async_sessionmaker(db_client.engine, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.email == "admin@museum.com")
        )
        admin_user = result.scalars().first()
        assert admin_user is not None
        return str(admin_user.id)


@pytest.fixture
async def db_session(db_client: DBClient):
    """
    Provides an AsyncSession for integration tests.
    """
    async_session = async_sessionmaker(db_client.engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def test_client(db_client: DBClient): # Depend on db_client to ensure DB is set up
    """
    Provides a Litestar AsyncTestClient for functional tests.
    Updates the app's state with the isolated db_client.
    """
    # We need to override the db_client in the app state for the test
    app.state.db_client = db_client
    
    async def get_test_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_sessionmaker(db_client.engine, expire_on_commit=False)() as session:
            yield session

    # Override the 'db_session' dependency which is what controllers/dependencies use
    # We save the original if strictly necessary, but for tests usually fine to just overwrite/restore
    
    # Note: Litestar v2 uses app.dependencies. We assume the key is 'db_session' matching the parameter name.
    # If the plugin uses a different mechanism, this might be tricky, but let's try 'db_session'.
    from litestar.di import Provide
    
    original_dep = app.dependencies.get("db_session")
    app.dependencies["db_session"] = Provide(get_test_db_session)
    
    async with AsyncTestClient(app=app) as client:
        yield client
    
    # Restore
    if original_dep:
        app.dependencies["db_session"] = original_dep
    else:
        del app.dependencies["db_session"]


@pytest.fixture
async def authenticated_test_client(test_client: AsyncTestClient, admin_user_id: str):
    """
    Provides a Litestar AsyncTestClient with X-User-ID header set.
    """
    test_client.headers["X-User-ID"] = admin_user_id
    return test_client