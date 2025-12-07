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
        self, data: MuseumCreate, db_session: AsyncSession, state: State
    ) -> MuseumRead:
        museum = await museum_repo.create_museum(db_session, data)
        
        # Send task to worker using the client in state
        worker_client: WorkerClient = state.worker_client
        await worker_client.send_task(
            queue_name="museum_tasks", 
            task_name="log_museum_created", 
            museum_id=str(museum.id), 
            city=museum.city
        )
        
        return museum

    @get("/")
    async def list_museums(self, db_session: AsyncSession) -> list[MuseumRead]:
        return await museum_repo.list_museums(db_session)