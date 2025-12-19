from litestar.connection import Request
from litestar.exceptions import NotAuthorizedException
from litestar.handlers import BaseRouteHandler


def admin_guard(connection: Request, _: BaseRouteHandler) -> None:
    # Middleware puts the user object in scope["user"]
    user = connection.scope.get("user")

    if not user.is_admin:
        raise NotAuthorizedException("User is not an admin")
