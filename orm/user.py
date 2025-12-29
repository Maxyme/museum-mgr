from uuid import UUID
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from orm.models.user import User
from api_models.user import ApiUserIn


async def create_user(session: AsyncSession, data: ApiUserIn) -> User:
    user = User(name=data.name, email=data.email, is_admin=data.is_admin)
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def get_user(session: AsyncSession, user_id: UUID) -> User | None:
    return await session.get(User, user_id)



async def list_users(session: AsyncSession) -> Sequence[User]:
    stmt = select(User)
    results = await session.execute(stmt)
    return results.scalars().all()


async def update_user(
    session: AsyncSession, user_id: UUID, data: ApiUserIn
) -> User | None:
    user = await get_user(session, user_id)
    if not user:
        return None

    if data.name is not None:
        user.name = data.name
    if data.email is not None:
        user.email = data.email
    if data.is_admin is not None:
        user.is_admin = data.is_admin

    await session.flush()
    return user