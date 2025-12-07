from typing import TYPE_CHECKING

from litestar import Litestar, get, post
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from litestar.status_codes import HTTP_201_CREATED
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession

from orm import museum as museum_repo
from clients.db_client import DBClient
from api_models.museum import MuseumCreate, MuseumRead
from controllers.health import HealthController

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AppSettings(BaseSettings):
    DB_URL: str


settings = AppSettings()

async def on_startup() -> None:
    db_client = DBClient(settings.DB_URL)
    await db_client.wait_for_db(timeout=5)


# Route
@post("/museums", status_code=HTTP_201_CREATED)
async def create_museum(
    data: MuseumCreate, db_session: AsyncSession
) -> MuseumRead:
    return await museum_repo.create_museum(db_session, data)


@get("/museums")
async def list_museums(db_session: AsyncSession) -> list[MuseumRead]:
    return await museum_repo.list_museums(db_session)


# Database Configuration
db_config = SQLAlchemyAsyncConfig(
    connection_string=settings.DB_URL,
    create_all=False,  # managed by alembic
    before_send_handler="autocommit",
)

# App
app = Litestar(
    route_handlers=[create_museum, list_museums, HealthController],
    plugins=[SQLAlchemyPlugin(config=db_config)],
    on_startup=[on_startup],
)
