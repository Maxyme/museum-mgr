import logging
import asyncio
import json
import asyncpg
from pgqueuer.db import AsyncpgDriver
from pgqueuer.models import Job
from pgqueuer.qm import QueueManager
from settings import settings

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

async def main2():
    # Use settings.DB_URL but ensure it's compatible with asyncpg (remove +asyncpg if present)
    db_url = settings.db_url# .replace("postgresql+asyncpg://", "postgresql://")

    # Extract connection params or just pass DSN
    # asyncpg.connect handles the DSN string well.

    logger.info(f"Connecting to {db_url}")
    connection = await asyncpg.connect(db_url)
    driver = AsyncpgDriver(connection)
    qm = QueueManager(driver)

    # Register entrypoints
    # We map the entrypoint name (string) to the function
    qm.entrypoint("log_museum_created")(log_museum_created)

    logger.info("Starting worker...")
    try:
        await qm.run()
    finally:
        await connection.close()




from datetime import datetime

import asyncpg
from pgqueuer import PgQueuer
from pgqueuer.db import AsyncpgDriver
from pgqueuer.models import Job, Schedule
from pgqueuer.__main__ import main

async def main() -> PgQueuer:
    db_url = settings.BROKER_URL
    conn = await asyncpg.connect(db_url)
    driver = AsyncpgDriver(conn)
    pgq = PgQueuer(driver)

    @pgq.entrypoint("fetch")
    async def process(job: Job) -> None:
        print(f"Processed: {job!r}")

    @pgq.schedule("every_minute", "* * * * *")
    async def every_minute(schedule: Schedule) -> None:
        print(f"Ran at {datetime.now():%H:%M:%S}")

    return pgq

if __name__ == "__main__":
    asyncio.run(main())