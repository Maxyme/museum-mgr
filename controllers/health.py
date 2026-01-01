"""Health checkpoints."""
from litestar import Controller, get
from litestar.status_codes import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE
from litestar.response import Response
from litestar.datastructures import State

from clients.db_client import DBClient
from clients.worker_client import WorkerClient


class HealthController(Controller):
    path = "/health"

    @get("/live")
    async def live(self) -> Response[dict[str, str]]:
        """Check if the worker is started."""
        return Response({"status": "ok"}, status_code=HTTP_200_OK)

    @get("/ready", status_code=HTTP_200_OK)
    async def ready(self, state: State) -> Response[dict[str, str]]:
        """Check if the server is ready to accept requests."""
        db_client: DBClient = state.db_client
        is_db_migrated = await db_client.check_migrations()
        if not is_db_migrated:
            return Response(
                {"status": "not ready", "detail": "db not migrated"},
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
            )

        worker_client: WorkerClient = state.worker_client
        is_worker_ready = await worker_client.get_num_tasks()
        if not is_worker_ready:
            return Response(
                {"status": "not ready", "detail": "worker not ready"},
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({"status": "ready"}, status_code=HTTP_200_OK)
