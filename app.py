from contextlib import asynccontextmanager

import uvicorn
import asyncpg
from litestar import Litestar
from litestar.di import Provide
from litestar.middleware import DefineMiddleware
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from litestar.datastructures import State

from clients.db_client import DBClient
from clients.worker_client import WorkerClient
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
    db_client = DBClient(db_url=settings.db_url)
    app.state.db_client = db_client
    yield
    
    # Teardown
    await db_client.close()

async def provide_worker_client(state: State) -> WorkerClient:
    """Provides a WorkerClient instance."""
    pool: asyncpg.Pool = state.pg_pool
    async with pool.acquire() as connection:
        driver = AsyncpgDriver(connection)
        qm = QueueManager(driver)
        yield WorkerClient(queue_manager=qm)


# Database Configuration
db_config = SQLAlchemyAsyncConfig(
    connection_string=settings.db_url,
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
        "worker_client": Provide(provide_worker_client)
    },
    exception_handlers={Exception: internal_server_error_handler},
)

def start_app():
    """Start api with uvicorn."""
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)

if __name__ == '__main__':
    start_app()