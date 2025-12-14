import logging
import asyncio
import json
import math
import signal
from pathlib import Path
from uuid import UUID

import asyncpg
import numpy as np
from onnxruntime import InferenceSession
from pgqueuer.db import AsyncpgDriver
from pgqueuer.models import Job
from pgqueuer import PgQueuer
from pgqueuer.queries import Queries
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

from settings import settings
from clients.db_client import DBClient
from orm.models.museum import Museum
from orm.models.city import City
from orm.models.visitor_prediction import VisitorPrediction

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)


async def upgrade_pgqueuer_schema(db_url: str):
    # Strip +asyncpg if present
    db_url_clean = db_url.replace("postgresql+asyncpg://", "postgresql://")

    logger.info(f"Upgrading pgqueuer schema to {db_url_clean}")
    conn = await asyncpg.connect(db_url_clean)
    try:
        queries = Queries.from_asyncpg_connection(conn)

        # Try to install first (for fresh DB)
        try:
            await queries.install()
            logger.info("PgQueuer schema installed successfully.")
        except asyncpg.exceptions.DuplicateObjectError:
            logger.info(
                "PgQueuer schema already exists (DuplicateObjectError). Skipping install."
            )
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"PgQueuer schema seems to exist ({e}). Skipping install.")
            else:
                # If install failed for other reasons, we re-raise
                logger.error(f"Failed to install schema: {e}")
                raise

        # Always run upgrade to ensure latest schema
        logger.info("Running pgqueuer upgrade...")
        await queries.upgrade()
        logger.info("PgQueuer schema upgrade completed.")

    finally:
        await conn.close()


async def main(db_manager: DBClient) -> PgQueuer:
    # Wait for the DB to be ready
    await db_manager.wait_for_db()

    # Install/upgrade pgqueuer schema
    await upgrade_pgqueuer_schema(settings.broker_url)

    # Load ONNX model
    model_path = Path("cache/model.onnx")
    session = None
    if not model_path.exists():
        logger.warning(f"Model not found at {model_path}. Prediction will fail.")
    else:
        try:
            session = InferenceSession(str(model_path))
            logger.info(f"Loaded ONNX model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")

    # Connect to the broker database
    db_url = settings.broker_url
    conn = await asyncpg.connect(db_url)
    driver = AsyncpgDriver(conn)
    pgq = PgQueuer(driver)

    # Session factory for Museum DB
    async_session = async_sessionmaker(db_manager.engine, expire_on_commit=False)

    async def log_museum_created(job: Job) -> None:
        try:
            data = json.loads(job.payload.decode())
            museum_id_str = data.get("museum_id")
            city_name = data.get("city")
            logger.info(
                f"Worker processing: Museum created in {city_name} with ID {museum_id_str}"
            )

            if not session:
                logger.warning("Skipping prediction: No ONNX session loaded.")
                return

            try:
                museum_id = UUID(museum_id_str)
            except ValueError:
                logger.error(f"Invalid museum ID: {museum_id_str}")
                return

            async with async_session() as db:
                async with db.begin():
                    # Fetch museum to get population
                    result = await db.execute(
                        select(Museum).where(Museum.id == museum_id)
                    )
                    museum = result.scalars().first()

                    if not museum:
                        logger.error(f"Museum {museum_id} not found in DB.")
                        return

                    population = museum.population

                    # Run Prediction
                    # Input name 'population' matches training script
                    x_input = np.array([[population]], dtype=np.int64)
                    output = session.run(None, {"population": x_input})
                    predicted_visitors = math.floor(float(output[0][0][0]))

                    logger.info(
                        f"Prediction for {city_name} (pop: {population}): {predicted_visitors}"
                    )

                    # Get or Create City
                    res_city = await db.execute(
                        select(City).where(City.name == city_name)
                    )
                    city_obj = res_city.scalars().first()

                    if not city_obj:
                        city_obj = City(name=city_name, population=population)
                        db.add(city_obj)
                        await db.flush()  # Flush to assign ID
                        logger.info(f"Created new City: {city_name}")

                    # Create VisitorPrediction
                    prediction = VisitorPrediction(
                        city_id=city_obj.id, predicted_visitors=predicted_visitors
                    )
                    db.add(prediction)

            logger.info(f"Saved prediction for {city_name}")

        except Exception as e:
            logger.error(f"Error processing job: {e}")

    # Register the entrypoint
    pgq.entrypoint("log_museum_created")(log_museum_created)

    return pgq


if __name__ == "__main__":

    async def run():
        # We use the Museum DB URL for the DB manager to check connectivity.
        db_manager = DBClient(db_url=settings.db_url)
        pgq_ref = {}

        loop = asyncio.get_running_loop()
        main_task = asyncio.current_task()

        def signal_handler():
            if pgq := pgq_ref.get("instance"):
                logger.info("Shutdown signal received. Stopping worker...")
                pgq.shutdown.set()
            else:
                logger.info("Shutdown signal received during startup. Cancelling...")
                main_task.cancel()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)

        try:
            pgq = await main(db_manager)
            pgq_ref["instance"] = pgq
            await pgq.run()
        except asyncio.CancelledError:
            logger.info("Worker cancelled.")
        finally:
            await db_manager.close()
            logger.info("Worker shutdown complete.")

    asyncio.run(run())
