import logging
import asyncio
import math
from pathlib import Path
from uuid import UUID

import numpy as np
from onnxruntime import InferenceSession
from taskiq_pg.psqlpy import PSQLPyBroker
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

from settings import settings
from clients.db_client import DBClient
from clients.worker_client import WorkerClient
from orm.models.museum import Museum
from orm.models.city import City
from orm.models.visitor_prediction import VisitorPrediction

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

_default_db_client = DBClient(settings.db_url)

# Taskiq broker
broker = PSQLPyBroker(url=settings.broker_url)
worker_client = WorkerClient(broker)

# Session factory for Museum DB
async_session = async_sessionmaker(_default_db_client.engine, expire_on_commit=False)

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


@broker.task(task_name="log_museum_created")
async def log_museum_created(museum_id: str, city: str) -> None:
    try:
        logger.info(
            f"Worker processing: Museum created in {city} with ID {museum_id}"
        )

        if not session:
            logger.warning("Skipping prediction: No ONNX session loaded.")
            return

        try:
            m_id = UUID(museum_id)
        except ValueError:
            logger.error(f"Invalid museum ID: {museum_id}")
            return

        async with async_session() as db:
            async with db.begin():
                # Fetch museum to get population
                result = await db.execute(
                    select(Museum).where(Museum.id == m_id)
                )
                museum = result.scalars().first()

                if not museum:
                    logger.error(f"Museum {m_id} not found in DB.")
                    return

                population = museum.population

                # Run Prediction
                # Input name 'population' matches training script
                x_input = np.array([[population]], dtype=np.int64)
                output = session.run(None, {"population": x_input})
                predicted_visitors = max(0, math.floor(float(output[0][0][0])))

                logger.info(
                    f"Prediction for {city} (pop: {population}): {predicted_visitors}"
                )

                # Get or Create City
                res_city = await db.execute(
                    select(City).where(City.name == city)
                )
                city_obj = res_city.scalars().first()

                if not city_obj:
                    city_obj = City(name=city, population=population)
                    db.add(city_obj)
                    await db.flush()  # Flush to assign ID
                    logger.info(f"Created new City: {city}")

                # Create VisitorPrediction
                prediction = VisitorPrediction(
                    city_id=city_obj.id, predicted_visitors=predicted_visitors
                )
                db.add(prediction)

        logger.info(f"Saved prediction for {city}")

    except Exception as e:
        logger.error(f"Error processing job: {e}")


async def startup():
    await _default_db_client.wait_for_db()
    await worker_client.startup()

async def shutdown():
    await worker_client.shutdown()
    await _default_db_client.close()

if __name__ == "__main__":
    # This is just for local testing, normally run with taskiq worker worker:broker
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        async def run_worker():
            await startup()
            # Taskiq worker is usually run via CLI, but for a simple script:
            logger.info("Worker started. Press Ctrl+C to stop.")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await shutdown()
        
        asyncio.run(run_worker())
