import math
from collections import defaultdict

import httpx
from bs4 import BeautifulSoup
import re
from multiprocessing import Pool

from data_science.constants import UNITS
from data_science.models import CityData, MuseumData

# Add Regex to remove parentheses and brackets and anything inside
NUMBER_REGEX = re.compile(r"\(.*?\)|\[.*?]")

headers = {"User-Agent": "Mozilla/5.0"}


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


def _make_httpx_request(url: str) -> httpx.Response:
    """Make an HTTPX GET request with headers."""
    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
    return response


def get_museum_visitors(museums_url: str) -> list[CityData]:
    """Scrapes the Wikipedia page for the list of most-visited museums."""

    with httpx.Client() as client:
        response = client.get(museums_url, headers=headers)
        response.raise_for_status()

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

    # todo: run loop in async tasks this for better performance
    cities_data = []
    urls = []
    for city_href, values in museums_data.items():
        # Fetch wikimedia entity for the city
        url_wikimedia = f"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&sites=enwiki&titles={city_href}&props=claims&languages=en"
        urls.append(url_wikimedia)

    with Pool(processes=10) as pool:
        wikimedia_responses = pool.map(_make_httpx_request, urls)

    # Process each city's wikimedia response
    for i, (city_href, values) in enumerate(museums_data.items()):
        wikimedia_response = wikimedia_responses[i]
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

        museums_list = [
            MuseumData(museum=m["museum"], visitors_per_year=m["visitors_per_year"])
            for m in values
        ]

        city_data = CityData(
            name=city_href,
            population=avg_population,
            visitors=avg_per_museum,
            museums=museums_list,
        )
        cities_data.append(city_data)

    return cities_data
