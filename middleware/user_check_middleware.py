from typing import TYPE_CHECKING
from uuid import UUID

from litestar.types import Scope, Receive, Send
from litestar.response import Response
from litestar.status_codes import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from orm.user import get_user

if TYPE_CHECKING:
    from clients.db_client import DBClient


class UserCheckMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        user_id_bytes = headers.get(b"x-user-id")

        if not user_id_bytes:
            response = Response(
                {"detail": "Missing X-User-ID header"},
                status_code=HTTP_401_UNAUTHORIZED,
            )
            await response(scope, receive, send)
            return

        try:
            user_id = UUID(user_id_bytes.decode("utf-8"))
        except ValueError:
            response = Response(
                {"detail": "Invalid X-User-ID header format"},
                status_code=HTTP_401_UNAUTHORIZED,
            )
            await response(scope, receive, send)
            return

        logger.info(f"Middleware Scope Keys: {scope.keys()}")

        db_client: "DBClient" | None = None
        if "state" in scope and "db_client" in scope["state"]:
            db_client = scope["state"]["db_client"]
        elif "app" in scope:
            db_client = getattr(scope["app"].state, "db_client", None)

        if not db_client:
            logger.error("DB Client not found in scope state or app state")
            response = Response(
                {"detail": "Server Configuration Error"},
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            )
            await response(scope, receive, send)
            return

        try:
            async with AsyncSession(db_client.engine) as session:
                user = await get_user(session, user_id)

                if not user:
                    response = Response(
                        {"detail": "User not found"}, status_code=HTTP_403_FORBIDDEN
                    )
                    await response(scope, receive, send)
                    return

                scope["user"] = user

        except Exception as e:
            logger.error(f"Auth Middleware DB Error: {e}")
            response = Response(
                {"detail": "Authentication Service Error"},
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
