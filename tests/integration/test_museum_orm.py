import pytest
from uuid import uuid4
from orm import museum as museum_repo
from tests.factories import MuseumCreateFactory


@pytest.mark.asyncio
async def test_create_museum(db_session):
    data = MuseumCreateFactory.build(city="Paris", population=2161000)
    museum = await museum_repo.create_museum(db_session, data, uuid4())
    await db_session.commit()

    assert museum.id is not None
    assert museum.city.name == "Paris"
    assert museum.population == 2161000


@pytest.mark.asyncio
async def test_list_museums(db_session):
    data1 = MuseumCreateFactory.build(city="Paris", population=2161000)
    data2 = MuseumCreateFactory.build(city="London", population=8982000)

    await museum_repo.create_museum(db_session, data1, uuid4())
    await museum_repo.create_museum(db_session, data2, uuid4())
    await db_session.commit()

    museums = await museum_repo.list_museums(db_session)
    assert len(museums) == 2
    cities = {m.city.name for m in museums}
    assert "Paris" in cities
    assert "London" in cities
