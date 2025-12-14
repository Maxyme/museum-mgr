from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api_models.museum import MuseumCreate
from orm.models.museum import Museum
from orm.models.city import City


async def create_museum(session: AsyncSession, data: MuseumCreate) -> Museum:
    # Check/Create City
    result = await session.execute(select(City).where(City.name == data.city))
    city = result.scalars().first()

    if not city:
        city = City(name=data.city, population=data.population)
        session.add(city)
        await session.flush()

    museum = Museum(city_id=city.id, population=data.population)
    session.add(museum)
    await session.flush()
    await session.refresh(museum)

    # Manually assign relationship for return (avoid extra DB hit if refresh doesn't do it)
    # But refresh doesn't load relationships unless requested.
    # We can set it directly since we have the object.
    museum.city = city

    return museum


async def list_museums(session: AsyncSession) -> Sequence[Museum]:
    result = await session.execute(select(Museum).options(joinedload(Museum.city)))
    return result.scalars().all()


async def get_museum(session: AsyncSession, museum_id: UUID) -> Museum | None:
    return await session.get(Museum, museum_id, options=[joinedload(Museum.city)])
