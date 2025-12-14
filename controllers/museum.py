from litestar import Controller, get, post
from litestar.status_codes import HTTP_201_CREATED
from litestar.datastructures import State
from sqlalchemy.ext.asyncio import AsyncSession

from orm import museum as museum_repo
from api_models.museum import MuseumCreate, MuseumRead
from clients.worker_client import WorkerClient


class MuseumController(Controller):
    path = "/museums"

    @post("/", status_code=HTTP_201_CREATED)
    async def create_museum(
        self, data: MuseumCreate, db_session: AsyncSession, worker_client: WorkerClient
    ) -> MuseumRead:
        museum = await museum_repo.create_museum(db_session, data)

        # Send task to worker
        # museum.city is a City object, we need to pass the name string
        await worker_client.log_museum_created(str(museum.id), museum.city.name)

        return MuseumRead.model_validate(museum)

    @get("/")
    async def list_museums(self, db_session: AsyncSession) -> list[MuseumRead]:
        museums = await museum_repo.list_museums(db_session)
        return [MuseumRead.model_validate(m) for m in museums]
