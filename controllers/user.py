from uuid import UUID

from litestar import Controller, get, post, patch
from litestar.status_codes import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from litestar.exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession
from litestar.di import Provide

from orm import user as user_repo
from api_models.user import UserCreate, UserRead, UserUpdate
from guards import admin_guard

class UserController(Controller):
    path = "/users"
    guards = [admin_guard]

    @post("/", status_code=HTTP_201_CREATED)
    async def create_user(
        self, data: UserCreate, db_session: AsyncSession
    ) -> UserRead:
        return await user_repo.create_user(db_session, data)

    @get("/")
    async def list_users(self, db_session: AsyncSession) -> list[UserRead]:
        return await user_repo.list_users(db_session)

    @get("/{user_id:uuid}")
    async def get_user(self, user_id: UUID, db_session: AsyncSession) -> UserRead:
        user = await user_repo.get_user(db_session, user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        return user

    @patch("/{user_id:uuid}")
    async def update_user(
        self, user_id: UUID, data: UserUpdate, db_session: AsyncSession
    ) -> UserRead:
        user = await user_repo.update_user(db_session, user_id, data)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        return user