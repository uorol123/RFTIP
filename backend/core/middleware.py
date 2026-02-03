"""
中间件模块 - Middleware Components

Provides custom middleware for request/response logging,
error tracking, and request context management.
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.logging import get_logger, log_request, log_security_event
from core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds request context to all requests.

    Features:
    - Generates unique request IDs
    - Adds request ID to response headers
    - Tracks request timing
    - Logs all requests and responses
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._request_start_times = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Record start time
        start_time = time.time()

        # Log incoming request
        client_host = request.client.host if request.client else "unknown"
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": client_host,
                "user_agent": request.headers.get("user-agent", "unknown"),
            }
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

            # Log response
            log_request(
                logger,
                request.method,
                request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                request_id=request_id,
                client_host=client_host,
            )

            return response

        except Exception as e:
            # Calculate duration for failed requests
            duration_ms = (time.time() - start_time) * 1000

            # Log the error
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                exc_info=e,
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                    "client_host": client_host,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )

            # Re-raise for global exception handler
            raise


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs security-related events.

    Tracks:
    - Failed authentication attempts
    - Permission denied errors
    - Suspicious request patterns
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Log failed authentication attempts
        if response.status_code == 401:
            request_id = getattr(request.state, "request_id", "unknown")
            client_host = request.client.host if request.client else "unknown"

            log_security_event(
                event_type="authentication_failed",
                ip_address=client_host,
                details={
                    "path": request.url.path,
                    "method": request.method,
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "request_id": request_id,
                }
            )

        # Log permission denied
        if response.status_code == 403:
            request_id = getattr(request.state, "request_id", "unknown")
            client_host = request.client.host if request.client else "unknown"

            log_security_event(
                event_type="permission_denied",
                ip_address=client_host,
                details={
                    "path": request.url.path,
                    "method": request.method,
                    "request_id": request_id,
                }
            )

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that catches and formats unhandled exceptions.

    Provides consistent error responses for unexpected errors.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            # This is a fallback - the global exception handler should catch most errors
            # This only handles errors that escape the exception handler
            request_id = getattr(request.state, "request_id", "unknown")

            logger.critical(
                f"Unhandled exception in middleware: {type(e).__name__}",
                exc_info=e,
                extra={"request_id": request_id}
            )

            # Return generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "detail": "Please try again later",
                    "request_id": request_id,
                }
            )


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs performance metrics for slow requests.

    Logs requests that take longer than the configured threshold.
    """

    def __init__(self, app: ASGIApp, slow_threshold_ms: float = 1000.0):
        super().__init__(app)
        self.slow_threshold_ms = slow_threshold_ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000

        # Log slow requests
        if duration_ms > self.slow_threshold_ms:
            request_id = getattr(request.state, "request_id", "unknown")
            client_host = request.client.host if request.client else "unknown"

            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} ({duration_ms:.2f}ms)",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                    "client_host": client_host,
                    "performance_warning": "slow_request",
                }
            )

        return response


class CORSMiddlewareWithLogging(BaseHTTPMiddleware):
    """
    Custom CORS middleware that logs CORS-related information.

    Note: FastAPI's built-in CORSMiddleware should still be used for actual CORS handling.
    This middleware only adds logging for debugging purposes.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        origin = request.headers.get("origin", "none")

        response = await call_next(request)

        # Log CORS requests
        if origin != "none":
            request_id = getattr(request.state, "request_id", "unknown")

            logger.debug(
                f"CORS request from origin: {origin}",
                extra={
                    "request_id": request_id,
                    "origin": origin,
                    "path": request.url.path,
                    "method": request.method,
                }
            )

        return response


def get_request_id(request: Request) -> str:
    """
    Helper function to get the request ID from the request state.

    Args:
        request: FastAPI request object

    Returns:
        Request ID string or "unknown" if not set
    """
    return getattr(request.state, "request_id", "unknown")


def get_client_ip(request: Request) -> str:
    """
    Helper function to get the client IP address.

    Checks X-Forwarded-For header for proxy scenarios.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address string
    """
    # Check for forwarded IP (behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct connection
    return request.client.host if request.client else "unknown"
