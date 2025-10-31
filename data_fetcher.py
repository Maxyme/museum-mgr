import math
from collections import defaultdict
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from peewee import *
import re
import json


# Add Regex to remove parentheses and brackets and anything inside
NUMBER_REGEX = re.compile(r"\(.*?\)|\[.*?\]")

MUSEUMS_URL = "https://en.wikipedia.org/wiki/List_of_most-visited_museums"

UNITS = {
    "million": 1000000,
}


def _parse_number_with_string_multiplier(text: str) -> int:
    """Parse number with string multiplier into int (ie million)."""
    local_multiplier = 1
    # Remove possible paratheses and brackets
    local_text = NUMBER_REGEX.sub("", text).strip().lower()

    # Replace any written units with multipliers
    for unit, multiplier in UNITS.items():
        if unit in text:
            local_text = text.replace(unit, "").strip()
            local_multiplier = multiplier
            break

    # replace commas with nothing (no floats expected)
    text_number = local_text.split(" ")[0].replace(",", "")

    # float to handle cases like "1.5 million"
    text_number = float(text_number)

    # Round down to nearest int
    return math.floor((text_number * local_multiplier))


def get_museum_visitors() -> dict:
    """Scrapes the Wikipedia page for the list of most-visited museums."""

    with httpx.Client() as client:
        response = client.get(MUSEUMS_URL)

    soup = BeautifulSoup(response.content, "html.parser")

    # Find the table in the page (skip the header row)
    table_el = soup.find("table")
    table_data = [[cell for cell in row("td")] for row in table_el("tr")[1:]]

    # Organize into dict of city -> museums, visitors
    museums_data = defaultdict(list)
    for row in table_data:
        museum = row[0].text.strip()
        visitors = _parse_number_with_string_multiplier(row[1].text)
        # city = row[2].text.strip().replace(",", "")
        city_href = row[2].contents[0].attrs["href"].lstrip("/wiki/")
        museum_data = {
            "museum": museum,
            "visitors_per_year": visitors,
        }
        # use the city href as key to prevent same-ish city names
        museums_data[city_href].append(museum_data)

    # todo: parallelize this
    pop_visitors = defaultdict(dict)
    for city_href, values in museums_data.items():
        # city_href = museum_data[city]["href"].lstrip("/wiki/")
        # url_wikimedia = f"https://www.wikidata.org/w/api.php?action=wbgetclaims&format=json&titles={city_href}&entity=Q90&property=P1082"
        url_wikimedia = f"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&sites=enwiki&titles={city_href}&props=claims&languages=en"

        with httpx.Client() as client:
            wikimedia_response = client.get(url_wikimedia)

        wikimedia_json = wikimedia_response.json()
        entities = wikimedia_json["entities"]

        # Use the first entity found which is the wikimedia entity for the city
        entity = next(iter(entities.values()))
        claims = entity["claims"]
        population_claims = claims["P1082"]

        # Average multiple population claims if more than one
        population_values = []
        for pop_claim in population_claims:
            pop_value = int(pop_claim["mainsnak"]["datavalue"]["value"]["amount"])
            population_values.append(pop_value)

        avg_population = math.floor(sum(population_values) / len(population_values))

        # Avg the visitors for the museums in that city
        total_visitors = sum(museum_data["visitors_per_year"] for museum_data in values)
        avg_per_museum = math.floor(total_visitors / len(values))

        pop_visitors[city_href]["population"] = avg_population
        pop_visitors[city_href]["visitors"] = avg_per_museum

    return pop_visitors


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
