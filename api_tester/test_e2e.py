from polyfactory.factories.pydantic_factory import ModelFactory
from models import MuseumCreate


class MuseumCreateFactory(ModelFactory[MuseumCreate]):
    __model__ = MuseumCreate


def test_create_and_list_museums(http_client):
    # Generate a new museum
    museum_data = MuseumCreateFactory.build()
    payload = museum_data.model_dump()
    response = http_client.post("/museums", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["city"] == payload["city"]
    assert created["population"] == payload["population"]
    assert "id" in created

    # Check that it appears in the list
    response = http_client.get("/museums")
    assert response.status_code == 200
    museums = response.json()
    assert len(museums) == 1
    found = any(m["id"] == created["id"] for m in museums)
    assert found, f"Created museum {created['id']} not found in list"
