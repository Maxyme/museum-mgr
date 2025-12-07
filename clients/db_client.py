import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

logger = logging.getLogger(__name__)

class DBClient:
    def __init__(self, db_url: str):
        self.db_url = db_url

    async def wait_for_db(self, timeout: int = 5) -> None:
        """
        Check if the database is ready by attempting to connect.
        
        Args:
            timeout: Maximum time to wait in seconds. Defaults to 5.
        """
        # Create a temporary engine just for the check
        engine = create_async_engine(self.db_url)
        start_time = asyncio.get_running_loop().time()
        
        logger.info("Waiting for database...")
        while True:
            try:
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                logger.info("Database is ready.")
                break
            except Exception as e:
                current_time = asyncio.get_running_loop().time()
                if current_time - start_time > timeout:
                    logger.error(f"Database wait timeout after {timeout}s: {e}")
                    await engine.dispose()
                    raise TimeoutError(f"Database unavailable after {timeout}s") from e
                
                await asyncio.sleep(0.5)
        
        await engine.dispose()

    async def clear_db(self) -> None:
        """
        Clear all data from the database, preserving the schema.
        Using CASCADE to handle foreign keys.
        """
        engine = create_async_engine(self.db_url)
        try:
            async with engine.begin() as conn:
                await conn.execute(text("DROP SCHEMA public CASCADE;"))
                await conn.execute(text("CREATE SCHEMA public;"))
            logger.info("Database schema dropped and recreated.")
        finally:
            await engine.dispose()

    async def create_all(self) -> None:
        """
        Create all tables defined in the metadata.
        """
        from api_models.museum import Museum
        metadata = Museum.metadata
        engine = create_async_engine(self.db_url)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(metadata.create_all)
            logger.info("Tables created.")
        finally:
            await engine.dispose()

    async def check_migrations(self) -> bool:
        """
        Check if the database is fully migrated.
        Returns True if the database is at the head revision, False otherwise.
        """
        from alembic import command, config
        from alembic.runtime import migration
        from alembic.script import ScriptDirectory
        from sqlalchemy import create_engine
        # Alembic is synchronous, so we run this in a separate thread or use sync engine for check
        # For simplicity in this context, we'll use a sync engine locally just for this check
        # as Alembic's internal API is sync.
        # Replace 'postgresql+asyncpg' with 'postgresql' for sync connection
        sync_url = self.db_url.replace("+asyncpg", "")

        def _check_sync():
            engine = create_engine(sync_url)
            alembic_cfg = config.Config("alembic.ini")
            script = ScriptDirectory.from_config(alembic_cfg)
            with engine.connect() as conn:
                context = migration.MigrationContext.configure(conn)
                current_rev = context.get_current_revision()
                head_rev = script.get_current_head()
                return current_rev == head_rev
        return await asyncio.to_thread(_check_sync)