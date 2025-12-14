import argparse
import json
from pathlib import Path
from onnxruntime import InferenceSession
from peewee import SqliteDatabase

from constants import MUSEUMS_URL
from data_science.data_science import get_museum_visitors
from db import create_and_populate_db
import polars as pl
from data_science.onnx_train_predict import train_model, predict

cache_path = Path(__file__).parent / "cache"
cache_path.mkdir(exist_ok=True)
museum_data_path = cache_path / "museum_data.json"
db_path = cache_path / "local.db"
sklearn_model_path = cache_path / "linear_regression_model.joblib"
onnx_model_path = cache_path / "model.onnx"


def main(population: int):
    # Check if the file already exists
    if not museum_data_path.exists():
        museum_data = get_museum_visitors(MUSEUMS_URL)

        # Dump to a json to file (as a cache)
        with museum_data_path.open("w") as handler:
            json.dump(museum_data, handler, indent=4)

    # Save into db if it doesn't exist
    db = SqliteDatabase(db_path)
    if not db_path.exists():
        create_and_populate_db(museum_data_path, db)

    # Check if the model exists
    if not onnx_model_path.exists():
        # Read the db to set the population and visitors data in a DataFrame
        # Filter outliers ("Vatican City Rome"...)
        df = pl.read_database(
            query="SELECT City.population, City.avg_museum_visitors_per_year FROM City WHERE City.population > 200_000",
            connection=db,
        )
        session = train_model(df, sklearn_model_path, onnx_model_path)
    else:
        session = InferenceSession(onnx_model_path)

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
