import json
from pathlib import Path

from peewee import SqliteDatabase, Model, CharField, IntegerField


def create_and_populate_db(file_path: Path, db: SqliteDatabase):
    """
    Creates the database and populates it with museum and city data.
    Uses parallel requests for faster population fetching.
    """

    class BaseModel(Model):
        class Meta:
            database = db

    class City(BaseModel):
        name = CharField(unique=True)
        population = IntegerField()
        avg_museum_visitors_per_year = IntegerField()

    db.connect(reuse_if_open=True)
    db.create_tables([City])

    # Load museum data from JSON file
    with open(file_path, "r") as f:
        museum_data = json.load(f)

    # Insert data
    for city_name, data in museum_data.items():
        # Insert or get city
        city, _ = City.get_or_create(
            name=city_name,
            population=data["population"],
            avg_museum_visitors_per_year=data["visitors"],
        )

    db.close()
