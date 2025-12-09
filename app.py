from contextlib import asynccontextmanager

import uvicorn
import asyncpg
from litestar import Litestar
from litestar.di import Provide
from litestar.middleware import DefineMiddleware
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from litestar.datastructures import State

from clients.db_client import DBClient
from controllers.health import HealthController
from controllers.museum import MuseumController
from controllers.user import UserController
from middleware.request_id_middleware import RequestIDMiddleware
from middleware.user_check_middleware import UserCheckMiddleware
from exception_handlers import internal_server_error_handler
from settings import settings
from pgqueuer.db import AsyncpgDriver
from pgqueuer.qm import QueueManager


@asynccontextmanager
async def lifespan(app: Litestar):
    db_client = DBClient(db_url=settings.DB_URL)
    app.state.db_client = db_client
    
    # Setup asyncpg pool for pgqueuer
    pg_url = settings.DB_URL.replace("postgresql+asyncpg://", "postgresql://")
    pool = await asyncpg.create_pool(pg_url)
    app.state.pg_pool = pool

    await db_client.wait_for_db(timeout=5)
    
    yield
    
    # Teardown
    await db_client.close()
    await pool.close()

async def provide_queue_manager(state: State) -> QueueManager:
    """Provides a QueueManager instance using a connection from the pool."""
    pool: asyncpg.Pool = state.pg_pool
    async with pool.acquire() as connection:
        driver = AsyncpgDriver(connection)
        yield QueueManager(driver)


# Database Configuration
db_config = SQLAlchemyAsyncConfig(
    connection_string=settings.DB_URL,
    create_all=False,  # managed by alembic
    before_send_handler="autocommit",
)

# App
app = Litestar(
    route_handlers=[MuseumController, HealthController, UserController],
    plugins=[SQLAlchemyPlugin(config=db_config)],
    lifespan=[lifespan],
    middleware=[
        LoggingMiddlewareConfig().middleware,
        DefineMiddleware(RequestIDMiddleware),
        DefineMiddleware(UserCheckMiddleware),
    ],
    dependencies={
        "queue_manager": Provide(provide_queue_manager)
    },
    exception_handlers={Exception: internal_server_error_handler},
)

def start_app():
    """Start api with uvicorn."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    start_app()
