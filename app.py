from typing import TYPE_CHECKING
from contextlib import asynccontextmanager

import uvicorn
from litestar import Litestar
from litestar.di import Provide
from litestar.middleware import DefineMiddleware
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from pydantic_settings import BaseSettings, SettingsConfigDict

from clients.db_client import DBClient
from clients.worker_client import WorkerClient
from controllers.health import HealthController
from controllers.museum import MuseumController
from controllers.user import UserController
from middleware.request_id_middleware import RequestIDMiddleware
from middleware.user_check_middleware import UserCheckMiddleware
from exception_handlers import internal_server_error_handler

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    DB_URL: str
    BROKER_URL: str

settings = Settings()

@asynccontextmanager
async def lifespan(app: Litestar):
    db_client = DBClient(db_url=settings.DB_URL) # Only pass URL
    worker_client = WorkerClient(broker_url=settings.BROKER_URL)
    app.state.db_client = db_client
    app.state.worker_client = worker_client
    await db_client.wait_for_db(timeout=5)
    yield
    # Teardown
    await db_client.close() # Call close on the client


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
    exception_handlers={Exception: internal_server_error_handler},
)

def start_app():
    """Start api with uvicorn."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    start_app()