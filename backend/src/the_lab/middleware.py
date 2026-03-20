"""Application middleware."""

import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Headers that may contain sensitive data and should not be logged
_SENSITIVE_HEADERS = frozenset({
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-csrf-token",
})

# Paths to exclude from request logging (e.g., health checks, docs)
_EXCLUDED_PATHS = frozenset({
    "/docs",
    "/redoc",
    "/openapi.json",
})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs HTTP request and response details via structlog."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path in _EXCLUDED_PATHS:
            return await call_next(request)

        logger = structlog.stdlib.get_logger("the_lab.middleware")

        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            query=str(request.query_params) if request.query_params else None,
            client_host=request.client.host if request.client else None,
        )

        return response
