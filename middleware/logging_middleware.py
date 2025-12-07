import uuid
from loguru import logger
from litestar.types import ASGIApp, Scope, Receive, Send

class LoguruMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())
        
        # Bind the request_id to the logger context for this async task
        with logger.contextualize(request_id=request_id):
            logger.info(f"Request started: {scope['method']} {scope['path']}")
            try:
                await self.app(scope, receive, send)
            except Exception as e:
                logger.error(f"Request failed: {e}")
                raise e
            finally:
                logger.info(f"Request finished: {scope['method']} {scope['path']}")
