import asyncio
from pathlib import Path
import polars as pl

from sqlalchemy.ext.asyncio import async_sessionmaker

from clients.db_client import DBClient
from data_science.data_fetcher import get_museum_visitors
from data_science.constants import MUSEUMS_URL
from data_science.onnx_train_predict import train_model
from settings import settings
from orm.city import get_or_create_city
from orm.museum import create_museum
from api_models.museum import MuseumCreate


def build_ml_model(data: list, model_path: Path):
    rows = []
    for c in data:
        rows.append(
            {"population": c.population, "avg_museum_visitors_per_year": c.visitors}
        )

    df = pl.DataFrame(rows)
    df = df.filter(pl.col("population") > 200_000)

    sklearn_path = model_path.with_suffix(".joblib")
    train_model(df, sklearn_path, model_path)


async def save_in_db(session, cities):
    """Save cities and museums in db."""
    async with session.begin():
        for city_data in cities:
            # Ensure city exists
            await get_or_create_city(session, city_data.name, city_data.population)

            # Create Museums
            for _ in city_data.museums:
                museum_data = MuseumCreate(
                    city=city_data.name, population=city_data.population
                )
                await create_museum(session, museum_data)


async def main():
    """Run full script to get onnx model."""
    cities = get_museum_visitors(MUSEUMS_URL)
    db_client = DBClient(settings.db_url)
    await db_client.wait_for_db()

    session_maker = async_sessionmaker(db_client.engine, expire_on_commit=False)
    async with session_maker() as session:
        await save_in_db(session, cities)

    model_path = Path("cache/model.onnx")
    model_path.parent.mkdir(exist_ok=True)
    build_ml_model(cities, model_path)

    await db_client.close()


if __name__ == "__main__":
    asyncio.run(main())
