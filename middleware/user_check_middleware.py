from typing import TYPE_CHECKING
from uuid import UUID

from litestar.middleware import MiddlewareProtocol
from litestar.types import ASGIApp, Scope, Receive, Send
from litestar.response import Response
from litestar.status_codes import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from sqlalchemy import select

if TYPE_CHECKING:
    from clients.db_client import DBClient

class UserCheckMiddleware(MiddlewareProtocol):
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        # Skip check for health endpoints
        if scope["path"].startswith("/health"):
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        # Headers are bytes
        user_id_bytes = headers.get(b"x-user-id")
        
        if not user_id_bytes:
            # If mandatory, reject. Assuming mandatory for secured routes.
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
        
        # We need to query the DB. 
        # Using the engine from db_client to check user existence.
        # This is async.
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
                
                # Optionally set user in scope/state for downstream
                # scope["user"] = user 
                
        except Exception as e:
            # Fallback for DB errors
            print(f"Auth Middleware DB Error: {e}")
            response = Response(
                {"detail": "Authentication Service Error"}, 
                status_code=HTTP_500_INTERNAL_SERVER_ERROR
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
