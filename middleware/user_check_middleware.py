from uuid import UUID

from litestar.exceptions import NotAuthorizedException
from litestar.middleware import ASGIMiddleware
from litestar.types import Scope, Receive, Send, ASGIApp


class UserCheckMiddleware(ASGIMiddleware):
    async def handle(
        self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp
    ) -> None:
        """Add the user_id to the request scope."""
        headers = dict(scope["headers"])
        user_id_bytes = headers.get(b"x-user-id")

        if not user_id_bytes:
            raise NotAuthorizedException(detail="Missing X-User-ID header")

        try:
            scope["user_id"] = UUID(user_id_bytes.decode("utf-8"))
        except ValueError:
            raise NotAuthorizedException(detail="Invalid X-User-ID header format")

        await next_app(scope, receive, send)
