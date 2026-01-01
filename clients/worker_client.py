from dataclasses import dataclass

from taskiq_pg.psqlpy import PSQLPyBroker
from worker import log_museum_created

@dataclass
class WorkerClient:
    broker: PSQLPyBroker

    async def startup(self) -> None:
        await self.broker.startup()

    async def shutdown(self) -> None:
        await self.broker.shutdown()

    async def create_museum_task(self, *, museum_id: str, city: str) -> None:
        task = await log_museum_created.kiq(museum_id, city)
        print(await task.wait_result())

    async def get_num_tasks(self) -> int:
        """Return num tasks."""
        all_tasks = self.broker.get_all_tasks()
        return len(all_tasks)


