import json
from pgqueuer.queries import Queries


class WorkerClient:
    def __init__(self, queries: Queries):
        self.queries = queries

    async def enqueue_job(self, entrypoint: str, payload: dict) -> None:
        encoded_payload = json.dumps(payload).encode()
        await self.queries.enqueue(
            entrypoint=[entrypoint],
            payload=[encoded_payload],
            priority=[0],
        )

    async def log_museum_created(self, museum_id: str, city: str) -> None:
        await self.enqueue_job(
            "log_museum_created", {"museum_id": museum_id, "city": city}
        )