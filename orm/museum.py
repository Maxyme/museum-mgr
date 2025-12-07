from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_models.museum import MuseumCreate
from orm.models.museum import Museum


async def create_museum(session: AsyncSession, data: MuseumCreate) -> Museum:
    museum = Museum(city=data.city, population=data.population)
    session.add(museum)
    return museum


async def list_museums(session: AsyncSession) -> Sequence[Museum]:
    result = await session.execute(select(Museum))
    return result.scalars().all()


async def get_museum(session: AsyncSession, museum_id: UUID) -> Museum | None:
    return await session.get(Museum, museum_id)
