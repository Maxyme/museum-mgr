from typing import TYPE_CHECKING
from uuid import UUID

from litestar.types import Scope, Receive, Send, ASGIApp
from litestar.exceptions import (
    NotAuthorizedException,
    PermissionDeniedException,
    InternalServerException,
)
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from orm.user import get_user

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
            raise NotAuthorizedException(detail="Missing X-User-ID header")

        try:
            user_id = UUID(user_id_bytes.decode("utf-8"))
        except ValueError:
            raise NotAuthorizedException(detail="Invalid X-User-ID header format")

        logger.info(f"Middleware Scope Keys: {scope.keys()}")

        # Get db client from state
        db_client: "DBClient" = scope["state"]["db_client"]

        async with AsyncSession(db_client.engine) as session:
            user = await get_user(session, user_id)

        if not user:
            raise PermissionDeniedException(detail="User not found")

        scope["user"] = user

        await self.app(scope, receive, send)