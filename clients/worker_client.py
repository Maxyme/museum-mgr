import json
from pgqueuer.qm import QueueManager


class WorkerClient:
    def __init__(self, queue_manager: QueueManager):
        self.queue_manager = queue_manager

    async def enqueue_job(self, entrypoint: str, payload: dict) -> None:
        encoded_payload = json.dumps(payload).encode()
        await self.queue_manager.queries.enqueue(
            entrypoint=[entrypoint], payload=[encoded_payload]
        )

    async def log_museum_created(self, museum_id: str, city: str) -> None:
        await self.enqueue_job(
            "log_museum_created", {"museum_id": museum_id, "city": city}
        )
