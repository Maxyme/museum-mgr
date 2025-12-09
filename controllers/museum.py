from litestar import Controller, get, post
from litestar.status_codes import HTTP_201_CREATED
from sqlalchemy.ext.asyncio import AsyncSession
import json
from typing import Any

from orm import museum as museum_repo
from api_models.museum import MuseumCreate, MuseumRead
# from pgqueuer.qm import QueueManager

class MuseumController(Controller):
    path = "/museums"

    @post("/", status_code=HTTP_201_CREATED)
    async def create_museum(
        self, 
        data: MuseumCreate, 
        db_session: AsyncSession, 
        queue_manager: Any
    ) -> MuseumRead:
        museum = await museum_repo.create_museum(db_session, data)
        
        # Send task to worker
        payload = json.dumps({
            "museum_id": str(museum.id),
            "city": museum.city
        }).encode()
        
        # queue_manager is Any, but we know it's QueueManager
        # Correct arguments for enqueue: entrypoint, payload
        await queue_manager.queries.enqueue(
            entrypoint=["log_museum_created"],
            payload=[payload]
        )
        
        return MuseumRead.model_validate(museum)

    @get("/")
    async def list_museums(self, db_session: AsyncSession) -> list[MuseumRead]:
        museums = await museum_repo.list_museums(db_session)
        return [MuseumRead.model_validate(m) for m in museums]