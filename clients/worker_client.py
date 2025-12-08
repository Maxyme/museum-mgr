import logging
import uuid
import asyncio
from dataclasses import dataclass
from asyncmq.backends.postgres import PostgresBackend

logger = logging.getLogger(__name__)

@dataclass
class WorkerClient:
    broker_url: str

    async def check_ready(self) -> bool:
        """
        Check if the broker is reachable.
        """
        try:
            dsn = self.broker_url.replace("+asyncpg", "")
            backend = PostgresBackend(dsn=dsn)
            await backend.connect()
            await backend.disconnect()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to broker: {e}")
            return False

    async def send_task(self, queue_name: str, task_name: str, **kwargs) -> None:
        """
        Send a task to the worker queue.
        """
        try:
            dsn = self.broker_url.replace("+asyncpg", "")
            backend = PostgresBackend(dsn=dsn)
            await backend.connect()
            
            payload = {
                "id": str(uuid.uuid4()),
                "task": task_name,
                "args": [],
                "kwargs": kwargs,
            }
            
            await backend.enqueue(queue_name, payload)
            await backend.disconnect()
        except Exception as e:
            logger.error(f"Failed to send task {task_name}: {e}")
            raise