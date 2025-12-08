import logging

from asyncmq.tasks import task
logger = logging.getLogger(__name__)

@task(queue="museums", retries=2, ttl=120)
async def log_museum_created(museum_id: str, city: str):
    logger.info(f"Worker processing: Museum created in {city} with ID {museum_id}")


#if __name__ == '__main__':
    # asyncmq worker start emails --concurrency 5
    # start asyncmq