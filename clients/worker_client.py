import json
from dataclasses import dataclass
from pgqueuer.qm import QueueManager


@dataclass
class WorkerClient:
    queue_manager: QueueManager

    async def enqueue_job(self, entrypoint: str, payload: dict) -> None:
        encoded_payload = json.dumps(payload).encode()
        await self.queue_manager.queries.enqueue(
            entrypoint=[entrypoint], payload=[encoded_payload]
        )

    async def log_museum_created(self, museum_id: str, city: str) -> None:
        await self.enqueue_job(
            "log_museum_created", {"museum_id": museum_id, "city": city}
        )
