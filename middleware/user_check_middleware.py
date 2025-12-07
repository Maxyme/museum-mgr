from typing import TYPE_CHECKING
from uuid import UUID

from litestar.middleware import ASGIMiddleware
from litestar.types import Scope, Receive, Send
from litestar.response import Response
from litestar.status_codes import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from sqlalchemy import select
from loguru import logger

if TYPE_CHECKING:
    from clients.db_client import DBClient

class UserCheckMiddleware(ASGIMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        user_id_bytes = headers.get(b"x-user-id")
        
        if not user_id_bytes:
            response = Response(
                {"detail": "Missing X-User-ID header"}, 
                status_code=HTTP_401_UNAUTHORIZED
            )
            await response(scope, receive, send)
            return

        try:
            user_id = UUID(user_id_bytes.decode("utf-8"))
        except ValueError:
            response = Response(
                {"detail": "Invalid X-User-ID header format"}, 
                status_code=HTTP_401_UNAUTHORIZED
            )
            await response(scope, receive, send)
            return

        db_client: "DBClient" = scope["state"]["db_client"]
        
        try:
            async with db_client.engine.connect() as conn:
                from api_models.user import User
                stmt = select(User).where(User.id == user_id)
                result = await conn.execute(stmt)
                user = result.scalars().first()
                
                if not user:
                    response = Response(
                        {"detail": "User not found"}, 
                        status_code=HTTP_403_FORBIDDEN
                    )
                    await response(scope, receive, send)
                    return
                
                scope["user"] = user
                
        except Exception as e:
            logger.error(f"Auth Middleware DB Error: {e}")
            response = Response(
                {"detail": "Authentication Service Error"}, 
                status_code=HTTP_500_INTERNAL_SERVER_ERROR
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
