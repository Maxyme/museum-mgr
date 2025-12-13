from litestar import Request, Response
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
from loguru import logger


def internal_server_error_handler(request: Request, exc: Exception) -> Response:
    """
    Handle all 500 errors, log them using the configured logger (Loguru),
    and return a generic error response.
    """
    logger.exception(f"Internal Server Error: {exc}")

    return Response(
        content={"status_code": 500, "detail": "Internal Server Error"},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )
