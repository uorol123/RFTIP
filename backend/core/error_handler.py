"""
全局异常处理器 - Global Exception Handlers

Provides centralized exception handling for the application.
Converts custom exceptions to standardized error responses.
"""
import logging
from datetime import datetime
from typing import Union
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from core.exceptions import (
    AppException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    ConflictException,
    ServerException,
    DatabaseException,
    FileProcessingException,
)
from core.logging import get_logger, log_error
from core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


def create_error_response(
    error_code: str,
    message: str,
    status_code: int,
    detail: Union[str, None] = None,
    errors: Union[list, None] = None,
    request_id: Union[str, None] = None,
    path: Union[str, None] = None,
    **extra_fields,
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        error_code: Machine-readable error identifier
        message: Human-readable error message
        status_code: HTTP status code
        detail: Additional error details
        errors: List of validation errors
        request_id: Request ID for tracking
        path: Request path
        **extra_fields: Additional fields to include in response

    Returns:
        JSONResponse with standardized error format
    """
    content = {
        "success": False,
        "error_code": error_code,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "status_code": status_code,
    }

    if detail:
        content["detail"] = detail

    if errors:
        content["errors"] = errors

    if request_id:
        content["request_id"] = request_id

    if path:
        content["path"] = path

    content.update(extra_fields)

    return JSONResponse(status_code=status_code, content=content)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI application.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handler for all custom AppException subclasses."""

        request_id = getattr(request.state, "request_id", "unknown")

        # Log the error
        logger.warning(
            f"Application error: {exc.error_code} - {exc.message}",
            extra={
                "request_id": request_id,
                "error_code": exc.error_code,
                "path": request.url.path,
                "method": request.method,
            }
        )

        return create_error_response(
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            detail=exc.detail,
            request_id=request_id,
            path=request.url.path,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handler for Pydantic validation errors."""

        request_id = getattr(request.state, "request_id", "unknown")

        # Format validation errors
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "code": error["type"],
            })

        # Log validation errors with details
        error_details = "\n  ".join([f"- {e['field']}: {e['message']} ({e['code']})" for e in errors])
        logger.warning(
            f"Validation error: {len(errors)} field(s)\n  {error_details}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "validation_errors": errors,
            }
        )

        return create_error_response(
            error_code="VALIDATION_ERROR",
            message="Validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please check your input and try again",
            errors=errors,
            request_id=request_id,
            path=request.url.path,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Handler for standard HTTP exceptions."""

        request_id = getattr(request.state, "request_id", "unknown")

        # Log HTTP errors (except 404 for static files)
        if exc.status_code != 404 or not request.url.path.startswith("/static"):
            logger.warning(
                f"HTTP error: {exc.status_code} - {exc.detail}",
                extra={
                    "request_id": request_id,
                    "status_code": exc.status_code,
                    "path": request.url.path,
                    "method": request.method,
                }
            )

        return create_error_response(
            error_code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            status_code=exc.status_code,
            request_id=request_id,
            path=request.url.path,
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Handler for database errors."""

        request_id = getattr(request.state, "request_id", "unknown")

        # Log database errors with full context
        log_error(logger, exc, {"path": request.url.path, "method": request.method}, request_id)

        # Check for integrity violations (unique constraints, foreign keys)
        if isinstance(exc, IntegrityError):
            return create_error_response(
                error_code="DATABASE_INTEGRITY_ERROR",
                message="Data integrity constraint violated",
                status_code=status.HTTP_409_CONFLICT,
                detail="The requested operation would violate data integrity",
                request_id=request_id,
                path=request.url.path,
            )

        # Generic database error
        return create_error_response(
            error_code="DATABASE_ERROR",
            message="A database error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Please try again later",
            request_id=request_id,
            path=request.url.path,
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handler for Pydantic model validation errors."""

        request_id = getattr(request.state, "request_id", "unknown")

        # Format validation errors
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "code": error["type"],
            })

        # Log validation errors with details
        error_details = "\n  ".join([f"- {e['field']}: {e['message']} ({e['code']})" for e in errors])
        logger.warning(
            f"Pydantic validation error: {len(errors)} error(s)\n  {error_details}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "validation_errors": errors,
            }
        )

        return create_error_response(
            error_code="VALIDATION_ERROR",
            message="Data validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The provided data is invalid",
            errors=errors,
            request_id=request_id,
            path=request.url.path,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Fallback handler for any unhandled exceptions.

        This should rarely be hit if proper error handling is in place.
        """

        request_id = getattr(request.state, "request_id", "unknown")

        # Log the unexpected error
        log_error(
            logger,
            exc,
            {
                "path": request.url.path,
                "method": request.method,
                "client_host": request.client.host if request.client else "unknown",
            },
            request_id,
        )

        # In development, include more details
        if settings.debug:
            return create_error_response(
                error_code="INTERNAL_SERVER_ERROR",
                message=f"Unexpected error: {type(exc).__name__}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
                request_id=request_id,
                path=request.url.path,
            )

        # In production, return generic error
        return create_error_response(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Please try again later or contact support",
            request_id=request_id,
            path=request.url.path,
        )


class ServiceException(AppException):
    """Exception for service-related errors (e.g., external APIs unavailable)."""

    def __init__(
        self,
        service_name: str,
        message: str = None,
        detail: str = None,
    ):
        self.service_name = service_name
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message=message or f"{service_name} service unavailable",
            error_code=f"{service_name.upper()}_SERVICE_UNAVAILABLE",
            detail=detail or f"The {service_name.lower()} service is temporarily unavailable",
        )
