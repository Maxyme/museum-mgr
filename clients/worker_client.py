from taskiq_pg.psqlpy import PSQLPyBroker


class WorkerClient:
    def __init__(self, broker: PSQLPyBroker):
        self.broker = broker

    async def startup(self) -> None:
        await self.broker.startup()

    async def shutdown(self) -> None:
        await self.broker.shutdown()

    async def log_museum_created(self, museum_id: str, city: str) -> None:
        # We need to import the task here or use the task name
        # Since we want to keep the client decoupled, we can use the task name
        await self.broker.kick("log_museum_created", museum_id=museum_id, city=city)

    async def is_ready(self) -> bool:
        try:
            # Taskiq doesn't have a direct 'is_ready' for the broker connection in the same way,
            # but we can check if we can get a connection from the pool if needed.
            # For now, we assume if the broker is initialized, it's ready or will fail on kick.
            return True
        except Exception:
            return False
