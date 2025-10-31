import argparse
import json
import polars as pl
from pathlib import Path

from onnxruntime import InferenceSession
from peewee import SqliteDatabase

from data_fetcher import create_and_populate_db, get_museum_visitors
from data_science import (
    get_linear_regression_model,
    predict,
)

museum_data_path = Path(__file__).parent / "museum_data.json"
db_path = Path(__file__).parent / "local.db"
model_path = Path(__file__).parent / "model.onnx"


def main(population: int):
    # Check if the file already exists
    if not museum_data_path.exists():
        museum_data = get_museum_visitors()

        # Dump to a json to file (as a cache)
        with museum_data_path.open("w") as handler:
            json.dump(museum_data, handler, indent=4)

    # Save into db if it doesn't exist
    db = SqliteDatabase(db_path)
    if not db_path.exists():
        create_and_populate_db(museum_data_path, db)

    # Check if the model exists
    if not model_path.exists():
        # Read the db to set the population and visitors data in a DataFrame
        # Filter outliers ("Vatican City Rome"...)
        df = pl.read_database(
            query="SELECT City.population, City.avg_museum_visitors_per_year FROM City WHERE City.population > 200_000",
            connection=db,
        )

        onnx_model = get_linear_regression_model(df)
        with open(model_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        # Todo: read from in-memory model instead
        session = InferenceSession(model_path)
    else:
        session = InferenceSession(model_path)

    # Use the model to predict visitors per year
    predicted_visitors = predict(session, population)
    print(f"predicted visitors per year: {predicted_visitors}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Predict museum visitors per year based on city population"
    )
    parser.add_argument(
        "input", type=int, help="Population of the city to predict for."
    )
    args = parser.parse_args()
    main(args.input)
