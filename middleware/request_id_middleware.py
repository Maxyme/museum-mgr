from uuid import uuid4
from litestar.middleware import ASGIMiddleware
from litestar.types import Scope, Receive, Send, ASGIApp
from loguru import logger


class RequestIDMiddleware(ASGIMiddleware):
    async def handle(
        self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp
    ) -> None:
        """Add a request id to incoming requests logs."""
        request_id = str(uuid4())
        with logger.contextualize(request_id=request_id):
            await next_app(scope, receive, send)
