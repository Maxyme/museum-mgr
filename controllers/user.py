from uuid import UUID

from litestar import Controller, get, post, patch
from litestar.status_codes import HTTP_201_CREATED
from litestar.exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from orm import user as user_repo
from api_models.user import ApiUserIn, ApiUserOut
from guards import admin_guard


class UserController(Controller):
    path = "/users"
    guards = [admin_guard]

    @post("/", status_code=HTTP_201_CREATED)
    async def create_user(
        self, data: ApiUserIn, db_session: AsyncSession
    ) -> ApiUserOut:
        user = await user_repo.create_user(db_session, data)
        return ApiUserOut.model_validate(user)

    @get("/")
    async def list_users(self, db_session: AsyncSession) -> list[ApiUserOut]:
        users = await user_repo.list_users(db_session)
        return [ApiUserOut.model_validate(u) for u in users]

    @get("/{user_id:uuid}")
    async def get_user(self, user_id: UUID, db_session: AsyncSession) -> ApiUserOut:
        user = await user_repo.get_user(db_session, user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        return ApiUserOut.model_validate(user)

    @get("whoami")
    async def whoami(self, scope: dict) -> ApiUserOut:
        """Return the current user."""
        return ApiUserOut.model_validate(scope.user)

    @patch("/{user_id:uuid}")
    async def update_user(
        self, user_id: UUID, data: ApiUserIn, db_session: AsyncSession
    ) -> ApiUserOut:
        user = await user_repo.update_user(db_session, user_id, data)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        return ApiUserOut.model_validate(user)
