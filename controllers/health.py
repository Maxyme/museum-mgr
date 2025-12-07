from litestar import Controller, get
from litestar.status_codes import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE
from litestar.response import Response
from litestar.datastructures import State
import asyncio

from clients.db_client import DBClient
from clients.worker_client import WorkerClient

class HealthController(Controller):
    path = "/health"

    @get("/live")
    async def live(self) -> Response[dict[str, str]]:
        return Response({"status": "ok"}, status_code=HTTP_200_OK)

    @get("/ready")
    async def ready(self, state: State) -> Response[dict[str, str]]:
        db_client: DBClient = state.db_client
        worker_client: WorkerClient = state.worker_client
        
        try:
            is_db_migrated = await db_client.check_migrations()
            is_worker_ready = await worker_client.check_ready()

            if is_db_migrated and is_worker_ready:
                return Response({"status": "ready"}, status_code=HTTP_200_OK)
            
            details = []
            if not is_db_migrated:
                details.append("Pending migrations")
            if not is_worker_ready:
                details.append("Worker/Broker not ready")

            return Response(
                {"status": "not ready", "detail": "; ".join(details)},
                status_code=HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"status": "error", "detail": str(e)},
                status_code=HTTP_503_SERVICE_UNAVAILABLE
            )