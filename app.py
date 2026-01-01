from contextlib import asynccontextmanager
from typing import Any
from uuid import UUID

import uvicorn
from litestar import Litestar
from litestar.di import Provide
from litestar.middleware import DefineMiddleware
from litestar.middleware.logging import LoggingMiddlewareConfig
from advanced_alchemy.extensions.litestar import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from litestar.exceptions import NotFoundException, PermissionDeniedException, NotAuthorizedException
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq_pg.psqlpy import PSQLPyBroker

from clients.db_client import DBClient
from clients.worker_client import WorkerClient
from controllers.health import HealthController
from controllers.museum import MuseumController
from controllers.user import UserController
from middleware.request_id_middleware import RequestIDMiddleware
from middleware.user_check_middleware import UserCheckMiddleware
from exception_handlers import (
    internal_server_error_handler,
    not_found_error_handler,
)
from settings import settings
from orm.user import get_user
from orm.models.user import User

# Initialize DBClient at module level or pass it to Litestar state
db_client = DBClient(db_url=settings.db_url)
broker = PSQLPyBroker(url=settings.broker_url)
worker_client = WorkerClient(broker)

@asynccontextmanager
async def lifespan(app: Litestar):
    app.state.db_client = db_client
    await worker_client.startup()
    app.state.worker_client = worker_client
    yield
    await worker_client.shutdown()
    await db_client.close()


# Database Configuration
db_config = SQLAlchemyAsyncConfig(
    connection_string=settings.db_url,
    create_all=False,  # managed by alembic
    before_send_handler="autocommit",
)

async def provide_user_id(scope: dict[str, Any]) -> UUID:
    user_id = scope.get("user_id")
    if not user_id:
        raise NotAuthorizedException(detail="Missing or invalid X-User-ID header")
    return user_id

async def provide_user(db_session: AsyncSession, user_id: UUID) -> User:
    user = await get_user(db_session, user_id)
    if not user:
        raise PermissionDeniedException(detail="User not found")
    return user

async def provide_worker_client(scope: dict[str, Any]) -> WorkerClient:
    return scope["state"]["worker_client"]

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
        "user_id": Provide(provide_user_id),
        "user": Provide(provide_user),
        "worker_client": Provide(provide_worker_client),
    },
    exception_handlers={
        Exception: internal_server_error_handler,
        NotFoundException: not_found_error_handler,
    },
)


def start_app():
    """Start api with uvicorn."""
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)


if __name__ == "__main__":
    start_app()
