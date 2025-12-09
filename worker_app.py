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

async def main():
    # Use settings.DB_URL but ensure it's compatible with asyncpg (remove +asyncpg if present)
    db_url = settings.DB_URL.replace("postgresql+asyncpg://", "postgresql://")
    
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

if __name__ == "__main__":
    asyncio.run(main())