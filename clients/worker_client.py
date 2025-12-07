import logging
import asyncio
from dataclasses import dataclass
from asyncmq import create_broker

logger = logging.getLogger(__name__)

@dataclass
class WorkerClient:
    broker_url: str

    async def check_ready(self) -> bool:
        """
        Check if the broker is reachable.
        """
        try:
            # We assume create_broker verifies connection
            await create_broker(self.broker_url)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to broker: {e}")
            return False

    async def send_task(self, queue_name: str, task_name: str, **kwargs) -> None:
        """
        Send a task to the worker queue.
        """
        try:
            broker = await create_broker(self.broker_url)
            await broker.send(queue_name, task_name, **kwargs)
        except Exception as e:
            logger.error(f"Failed to send task {task_name}: {e}")
            raise