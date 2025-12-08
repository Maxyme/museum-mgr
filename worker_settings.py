from asyncmq.backends.postgres import PostgresBackend
from asyncmq.conf.global_settings import Settings

from settings import settings


class AsyncMQSettings(Settings):
    # Use Redis at a custom URL
    backend = PostgresBackend(dsn=settings.DB_URL)
    # Increase default worker concurrency
    worker_concurrency = 1
    # Enable debug mode for verbose logging
    debug = True