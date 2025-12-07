from typing import TYPE_CHECKING
from contextlib import asynccontextmanager

from litestar import Litestar
from litestar.middleware import DefineMiddleware
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine # This import might be removed if not used for plugin config

from clients.db_client import DBClient
from clients.worker_client import WorkerClient
from controllers.health import HealthController
from controllers.museum import MuseumController
from controllers.user import UserController
from middleware.custom_middleware import RequestIDMiddleware, UserCheckMiddleware
from exception_handlers import internal_server_error_handler

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AppSettings(BaseSettings):
    DB_URL: str
    BROKER_URL: str

settings = AppSettings()


@asynccontextmanager
async def lifespan(app: Litestar):
    # Setup
    db_client = DBClient(db_url=settings.DB_URL) # Only pass URL
    worker_client = WorkerClient(broker_url=settings.BROKER_URL)
    
    app.state.db_client = db_client
    app.state.worker_client = worker_client
    
    # Wait for DB to be ready - Implicitly handled by client methods now, 
    # but explicitly waiting once on startup is still good to fail fast before serving requests.
    # I'll keep it for the app startup check, but the decorator ensures safety for individual calls.
    await db_client.wait_for_db(timeout=5)
    
    yield
    
    # Teardown
    await db_client.close() # Call close on the client
    # No explicit engine.dispose() here as DBClient manages it


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
        RequestIDMiddleware,
        DefineMiddleware(UserCheckMiddleware, exclude=["/health/live", "/health/ready"])
    ],
    exception_handlers={Exception: internal_server_error_handler},
)
