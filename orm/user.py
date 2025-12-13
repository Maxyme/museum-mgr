from uuid import UUID
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from orm.models.user import User
from api_models.user import UserCreate, UserUpdate


async def create_user(session: AsyncSession, data: UserCreate) -> User:
    user = User(name=data.name, email=data.email, is_admin=data.is_admin)
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def get_user(session: AsyncSession, user_id: UUID) -> User | None:
    return await session.get(User, user_id)


async def list_users(session: AsyncSession) -> Sequence[User]:
    result = await session.execute(select(User))
    return result.scalars().all()


async def update_user(
    session: AsyncSession, user_id: UUID, data: UserUpdate
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

    # stmt = update(User).where(User.id == user_id).values({"name": data.name, "email": data.email, "is_admin": data.is_admin})
    # await session.query(Stuff).update({Stuff.foo: Stuff.foo + 1})

    return user
