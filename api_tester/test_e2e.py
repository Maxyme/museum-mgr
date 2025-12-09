from polyfactory.factories.pydantic_factory import ModelFactory
from models import MuseumCreate

class MuseumCreateFactory(ModelFactory[MuseumCreate]):
    __model__ = MuseumCreate

def test_create_and_list_museums(http_client):
    # Generate random museum data
    museum_data = MuseumCreateFactory.build()
    payload = museum_data.model_dump()
    print(f"Testing with museum: {payload}")

    # Create
    response = http_client.post("/museums", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["city"] == payload["city"]
    assert created["population"] == payload["population"]
    assert "id" in created

    # List
    response = http_client.get("/museums")
    assert response.status_code == 200
    museums = response.json()
    assert isinstance(museums, list)
    
    # Verify our created museum is in the list
    found = any(m["id"] == created["id"] for m in museums)
    assert found, f"Created museum {created['id']} not found in list"
