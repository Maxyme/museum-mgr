from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from orm.models.city import City


async def get_or_create_city(session: AsyncSession, name: str, population: int) -> City:
    result = await session.execute(select(City).where(City.name == name))
    city = result.scalars().first()

    if not city:
        city = City(name=name, population=population)
        session.add(city)
        await session.flush()

    return city
