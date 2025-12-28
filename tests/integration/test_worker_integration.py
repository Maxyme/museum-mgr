import asyncio
import pytest
import asyncpg
from litestar.status_codes import HTTP_201_CREATED
from settings import settings
from worker_app import main as worker_main
from clients.db_client import DBClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_museum_creation_triggers_worker(authenticated_test_client):
    # Start the worker
    db_manager = DBClient(db_url=settings.db_url)
    pgq = await worker_main(db_manager)

    # Run worker in background
    worker_task = asyncio.create_task(pgq.run())

    try:
        # 1. Call API to create museum
        response = await authenticated_test_client.post(
            "/museums", json={"city": "Integration City", "population": 100000}
        )
        assert response.status_code == HTTP_201_CREATED

        # 2. Wait for job to be processed
        # We poll the pgqueuer_log table in broker_db (since pgqueuer table might be cleared)
        broker_url = settings.broker_url.replace("+asyncpg", "")
        broker_conn = await asyncpg.connect(broker_url)
        try:
            # Wait up to 5 seconds for the job to be marked as successful
            for _ in range(10):
                row = await broker_conn.fetchrow(
                    "SELECT status FROM pgqueuer_log WHERE entrypoint = $1 AND status = 'successful' ORDER BY id DESC LIMIT 1",
                    "log_museum_created",
                )
                if row:
                    break
                await asyncio.sleep(0.5)
            else:
                # If we timeout, we inspect what happened
                row = await broker_conn.fetchrow(
                    "SELECT * FROM pgqueuer_log ORDER BY id DESC LIMIT 1"
                )
                pytest.fail(
                    f"Worker did not process the job in time. Last log entry: {row}"
                )
        finally:
            await broker_conn.close()

    finally:
        # Stop worker gracefully
        pgq.shutdown.set()
        try:
            await asyncio.wait_for(worker_task, timeout=5.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass

        await db_manager.close()
