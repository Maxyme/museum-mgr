import logging
import asyncio
import json
import asyncpg
from pgqueuer.db import AsyncpgDriver
from pgqueuer.models import Job
from pgqueuer import PgQueuer

from settings import settings
from clients.db_client import DBClient

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)


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
            # await pgq.upgrade()
            await pgq.run()
        finally:
            await db_manager.close()

    asyncio.run(run())
