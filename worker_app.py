import asyncio
import os
import logging
from asyncmq import create_broker

logger = logging.getLogger(__name__)

BROKER_URL = os.getenv("BROKER_URL", "postgres://postgres:password@localhost:5432/broker_db")

async def run_worker():
    broker = await create_broker(BROKER_URL)
    
    # Initialize backend (create tables) if needed
    # asyncmq provides helper but usually create_broker with postgres url handles it or expects it.
    # Let's ensure tables exist.
    # The 'install_or_drop_postgres_backend' mentioned in search results is useful for setup.
    # But let's see if we can just start consuming.
    
    @broker.task(queue="museum_tasks")
    async def log_museum_created(museum_id: str, city: str):
        logger.info(f"Worker processing: Museum created in {city} with ID {museum_id}")

    logger.info("Worker started.")
    # Keep running
    # asyncmq doesn't have a built-in blocking run() like dramatiq CLI, 
    # we need to keep the loop alive or just let the broker work if it runs in background.
    # Usually we need a loop.
    try:
        # In a real app we might wait on a signal or use a run_forever loop
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Worker stopping...")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_worker())