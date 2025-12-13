import asyncio
import logging
from dataclasses import dataclass, field
from functools import wraps

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy import text, select
from sqlalchemy import create_engine

from api_models.base import Base
from orm.models.user import User

logger = logging.getLogger(__name__)


def ensure_db_ready(func):
    """
    Decorator to ensure the database is ready before executing the method.
    It calls wait_for_db on the instance.
    """

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        # Avoid infinite recursion if ensuring ready on wait_for_db itself (not needed there)
        await self.wait_for_db()
        return await func(self, *args, **kwargs)

    return wrapper


@dataclass
class DBClient:
    db_url: str
    engine: AsyncEngine = field(init=False)

    def __post_init__(self):
        self.engine = create_async_engine(self.db_url)
        logger.info("DBClient engine initialized.")

    async def close(self) -> None:
        if self.engine:
            await self.engine.dispose()
            logger.info("DBClient engine disposed.")

    async def wait_for_db(self, timeout: int = 5) -> None:
        start_time = asyncio.get_running_loop().time()

        # logger.info("Waiting for database...") # Reduced logging noise for decorator use
        while True:
            try:
                async with self.engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                # logger.info("Database is ready.")
                break
            except Exception as e:
                current_time = asyncio.get_running_loop().time()
                if current_time - start_time > timeout:
                    logger.error(f"Database wait timeout after {timeout}s: {e}")
                    raise TimeoutError(f"Database unavailable after {timeout}s") from e

                await asyncio.sleep(0.5)

    @ensure_db_ready
    async def clear_db(self) -> None:
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("DROP SCHEMA public CASCADE;"))
                await conn.execute(text("CREATE SCHEMA public;"))
            logger.info("Database schema dropped and recreated.")
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            raise

    @ensure_db_ready
    async def create_all(self) -> None:
        # Use Base.metadata which now includes both Museum and User
        metadata = Base.metadata

        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(metadata.create_all)
            logger.info("Tables created.")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    # check_migrations uses a sync engine internally and manages its own connection,
    # so we might not strictily need the async wait here, but it's good practice to ensure DB is up.
    # However, since check_migrations creates a separate sync engine, waiting on the async engine
    # ensures the server is reachable.
    @ensure_db_ready
    async def check_migrations(self) -> bool:
        from alembic import config
        from alembic.runtime import migration
        from alembic.script import ScriptDirectory

        sync_url = self.db_url.replace("+asyncpg", "")

        def _check_sync():
            engine = create_engine(sync_url)
            try:
                alembic_cfg = config.Config("alembic.ini")
                script = ScriptDirectory.from_config(alembic_cfg)

                with engine.connect() as conn:
                    context = migration.MigrationContext.configure(conn)
                    current_rev = context.get_current_revision()
                    head_rev = script.get_current_head()

                    return current_rev == head_rev
            finally:
                engine.dispose()

        return await asyncio.to_thread(_check_sync)

    @ensure_db_ready
    async def seed_db(self) -> None:
        """Seeds the database with an initial user."""
        try:
            # We need a session to add ORM objects
            session_maker = async_sessionmaker(self.engine, expire_on_commit=False)
            async with session_maker() as session:
                async with session.begin():
                    # Check if any user exists
                    result = await session.execute(select(User))
                    if result.scalars().first():
                        logger.info("Database already contains users. Skipping seed.")
                        return

                    # Create a default user
                    new_user = User(
                        name="Admin User", email="admin@museum.com", is_admin=True
                    )
                    session.add(new_user)

            logger.info(
                f"Database seeded with user: {new_user.name} ({new_user.email})"
            )
            return new_user
        except Exception as e:
            logger.error(f"Failed to seed database: {e}")
            raise
