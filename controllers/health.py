from litestar import Controller, get
from litestar.status_codes import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE
from litestar.response import Response
from litestar.datastructures import State
import asyncpg

from clients.db_client import DBClient


class HealthController(Controller):
    path = "/health"

    @get("/live")
    async def live(self) -> Response[dict[str, str]]:
        return Response({"status": "ok"}, status_code=HTTP_200_OK)

    @get("/ready")
    async def ready(self, state: State) -> Response[dict[str, str]]:
        db_client: DBClient = state.db_client
        pool: asyncpg.Pool = state.pg_pool

        try:
            is_db_migrated = await db_client.check_migrations()

            # Check worker DB connection and schema existence
            is_worker_ready = False
            try:
                async with pool.acquire() as conn:
                    # Check connection and if pgqueuer table exists
                    # This implies schema is installed and queue is ready
                    # Todo, worker client should have api check for live instead
                    await conn.execute("SELECT 1 FROM pgqueuer LIMIT 1")
                is_worker_ready = True
            except Exception:
                is_worker_ready = False

            if is_db_migrated and is_worker_ready:
                return Response({"status": "ready"}, status_code=HTTP_200_OK)

            details = []
            if not is_db_migrated:
                details.append("Pending migrations")
            if not is_worker_ready:
                details.append(
                    "Worker queue not ready (DB connection failed or schema missing)"
                )

            return Response(
                {"status": "not ready", "detail": "; ".join(details)},
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            return Response(
                {"status": "error", "detail": str(e)},
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
            )
