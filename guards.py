from litestar.connection import Request
from litestar.exceptions import NotAuthorizedException
from litestar.handlers import BaseRouteHandler
from sqlalchemy.ext.asyncio import AsyncSession
from orm.models.user import User


async def admin_guard(connection: Request, _: BaseRouteHandler) -> None:
    user_id = connection.scope.get("user_id")
    
    if not user_id:
         # Should have been caught by middleware, but safe to check
         raise NotAuthorizedException("User ID not found")

    db_client = connection.app.state.db_client
    async with AsyncSession(db_client.engine) as session:
        user = await session.get(User, user_id)
        if not user or not user.is_admin:
            raise NotAuthorizedException("User is not an admin")
        
        # Put user object in scope for handlers like whoami
        connection.scope["user"] = user
