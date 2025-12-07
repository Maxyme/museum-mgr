import pytest
from litestar.status_codes import HTTP_201_CREATED, HTTP_200_OK

@pytest.mark.asyncio
async def test_create_museum_api(test_client):
    response = await test_client.post(
        "/museums",
        json={"city": "New York", "population": 8419000}
    )
    assert response.status_code == HTTP_201_CREATED
    data = response.json()
    assert data["city"] == "New York"
    assert "id" in data

@pytest.mark.asyncio
async def test_list_museums_api(test_client):
    # Create a museum first
    await test_client.post(
        "/museums",
        json={"city": "Berlin", "population": 3645000}
    )

    response = await test_client.get("/museums")
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["city"] == "Berlin"
