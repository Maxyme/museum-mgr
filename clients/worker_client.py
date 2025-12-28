import json
import asyncpg
from pgqueuer.db import AsyncpgDriver
from pgqueuer.queries import Queries


class WorkerClient:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def enqueue_job(self, entrypoint: str, payload: dict) -> None:
        encoded_payload = json.dumps(payload).encode()
        async with self.pool.acquire() as connection:
            driver = AsyncpgDriver(connection)
            queries = Queries(driver)
            await queries.enqueue(
                entrypoint=[entrypoint],
                payload=[encoded_payload],
                priority=[0],
            )

    async def log_museum_created(self, museum_id: str, city: str) -> None:
        await self.enqueue_job(
            "log_museum_created", {"museum_id": museum_id, "city": city}
        )

    async def is_ready(self) -> bool:
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1 FROM pgqueuer LIMIT 1")
            return True
        except Exception:
            return False
