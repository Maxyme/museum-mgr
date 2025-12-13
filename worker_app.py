import logging
import asyncio
import json
import asyncpg
from pgqueuer.db import AsyncpgDriver
from pgqueuer.models import Job
from pgqueuer import PgQueuer
from pgqueuer.queries import Queries

from settings import settings
from clients.db_client import DBClient

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

async def upgrade_pgqueuer_schema(db_url: str):
    """Create/Upgrade schema on start."""
    # Strip +asyncpg if present
    db_url_clean = db_url.replace("postgresql+asyncpg://", "postgresql://")

    logger.info(f"Upgrading pgqueuer schema to {db_url_clean}")
    conn = await asyncpg.connect(db_url_clean)
    try:
        queries = Queries.from_asyncpg_connection(conn)

        # Try to install first (for fresh DB)
        try:
            await queries.install()
            logger.info("PgQueuer schema installed successfully.")
        except asyncpg.exceptions.DuplicateObjectError:
            logger.info("PgQueuer schema already exists (DuplicateObjectError). Skipping install.")
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"PgQueuer schema seems to exist ({e}). Skipping install.")
            else:
                # If install failed for other reasons, we re-raise
                logger.error(f"Failed to install schema: {e}")
                raise

        # Always run upgrade to ensure latest schema
        logger.info("Running pgqueuer upgrade...")
        await queries.upgrade()
        logger.info("PgQueuer schema upgrade completed.")

    finally:
        await conn.close()

async def log_museum_created(job: Job) -> None:
    try:
        data = json.loads(job.payload.decode())
        museum_id = data.get("museum_id")
        city = data.get("city")
        logger.info(f"Worker processing: Museum created in {city} with ID {museum_id}")
    except Exception as e:
        logger.error(f"Error processing job: {e}")

async def main(db_manager: DBClient) -> PgQueuer:
    # Wait for the DB to be ready
    await db_manager.wait_for_db()

    # Install/upgrade pgqueuer schema
    await upgrade_pgqueuer_schema(settings.broker_url)

    # Connect to the broker database
    db_url = settings.broker_url
    conn = await asyncpg.connect(db_url)
    driver = AsyncpgDriver(conn)
    pgq = PgQueuer(driver)

    # Register the entrypoint
    pgq.entrypoint("log_museum_created")(log_museum_created)

    return pgq

if __name__ == "__main__":
    async def run():
        # We use the Museum DB URL for the DB manager to check connectivity.
        db_manager = DBClient(db_url=settings.db_url)
        try:
            pgq = await main(db_manager)
            await pgq.run()
        finally:
            await db_manager.close()

    asyncio.run(run())