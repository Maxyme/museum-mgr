from uuid import uuid4
from litestar.types import Scope, Receive, Send
from loguru import logger

class RequestIDMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            request_id = str(uuid4())
            # Inject into scope so other middleware/handlers can access it if needed
            scope["request_id"] = request_id
            
            # Contextualize loguru
            with logger.contextualize(request_id=request_id):
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)
