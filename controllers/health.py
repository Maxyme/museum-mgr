from litestar import Controller, get
from litestar.status_codes import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE
from litestar.response import Response

from clients.db_client import DBClient
from api_app import settings

class HealthController(Controller):
    path = "/health"

    @get("/live")
    async def live(self) -> Response[dict[str, str]]:
        return Response({"status": "ok"}, status_code=HTTP_200_OK)

    @get("/ready")
    async def ready(self) -> Response[dict[str, str]]:
        client = DBClient(settings.DB_URL)
        try:
            is_migrated = await client.check_migrations()
            if is_migrated:
                return Response({"status": "ready"}, status_code=HTTP_200_OK)
            else:
                return Response(
                    {"status": "not ready", "detail": "Pending migrations"},
                    status_code=HTTP_503_SERVICE_UNAVAILABLE
                )
        except Exception as e:
            return Response(
                {"status": "error", "detail": str(e)},
                status_code=HTTP_503_SERVICE_UNAVAILABLE
            )
