"""
自定义异常类 - Custom Exception Classes

Defines application-specific exceptions for better error handling
and user-friendly error messages.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    """
    Base exception class for all application errors.

    Provides consistent error response structure with:
    - error_code: Machine-readable error identifier
    - message: Human-readable error message
    - detail: Additional error details (optional)
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: str = "APP_ERROR",
        detail: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail or message)
        self.error_code = error_code
        self.message = message
        self.headers = headers


class ValidationException(AppException):
    """
    Raised when input validation fails.

    HTTP 400 Bad Request
    """

    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        detail: Optional[str] = None,
    ):
        error_code = "VALIDATION_ERROR"
        if field:
            error_code = f"VALIDATION_ERROR.{field.upper()}"

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            error_code=error_code,
            detail=detail,
        )


class AuthenticationException(AppException):
    """
    Raised when authentication fails.

    HTTP 401 Unauthorized
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            error_code="AUTHENTICATION_FAILED",
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredException(AuthenticationException):
    """Raised when JWT token has expired."""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            message="Token has expired",
            detail=detail or "Your session has expired. Please login again.",
        )
        self.error_code = "TOKEN_EXPIRED"


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid."""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            message="Invalid token",
            detail=detail or "The provided token is invalid.",
        )
        self.error_code = "INVALID_TOKEN"


class AuthorizationException(AppException):
    """
    Raised when user lacks permission for an action.

    HTTP 403 Forbidden
    """

    def __init__(
        self,
        message: str = "Permission denied",
        required_permission: Optional[str] = None,
        detail: Optional[str] = None,
    ):
        error_code = "PERMISSION_DENIED"
        if required_permission:
            error_code = f"PERMISSION_DENIED.{required_permission.upper()}"

        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            error_code=error_code,
            detail=detail,
        )


class ResourceNotFoundException(AppException):
    """
    Raised when a requested resource doesn't exist.

    HTTP 404 Not Found
    """

    def __init__(
        self,
        resource_type: str = "Resource",
        resource_id: Optional[Any] = None,
        detail: Optional[str] = None,
    ):
        message = f"{resource_type} not found"
        if resource_id:
            message = f"{resource_type} with ID '{resource_id}' not found"

        error_code = f"NOT_FOUND.{resource_type.upper().replace(' ', '_')}"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            error_code=error_code,
            detail=detail,
        )


class UserNotFoundException(ResourceNotFoundException):
    """Raised when a user is not found."""

    def __init__(self, user_id: Optional[int] = None, username: Optional[str] = None):
        if username:
            message = f"User '{username}' not found"
            detail = f"No user found with username '{username}'"
        elif user_id:
            message = f"User with ID {user_id} not found"
            detail = f"No user found with ID {user_id}"
        else:
            message = "User not found"
            detail = "The specified user does not exist"

        super().__init__(
            resource_type="User",
            resource_id=user_id or username,
            detail=detail,
        )
        self.error_code = "USER_NOT_FOUND"
        self.message = message


class FileNotFoundException(ResourceNotFoundException):
    """Raised when a file is not found."""

    def __init__(self, file_id: Optional[int] = None, filename: Optional[str] = None):
        if filename:
            message = f"File '{filename}' not found"
            detail = f"No file found with filename '{filename}'"
        elif file_id:
            message = f"File with ID {file_id} not found"
            detail = f"No file found with ID {file_id}"
        else:
            message = "File not found"
            detail = "The specified file does not exist"

        super().__init__(
            resource_type="File",
            resource_id=file_id or filename,
            detail=detail,
        )
        self.error_code = "FILE_NOT_FOUND"
        self.message = message


class ConflictException(AppException):
    """
    Raised when a request conflicts with existing data.

    HTTP 409 Conflict
    """

    def __init__(
        self,
        message: str = "Resource conflict",
        conflict_type: Optional[str] = None,
        detail: Optional[str] = None,
    ):
        error_code = "CONFLICT"
        if conflict_type:
            error_code = f"CONFLICT.{conflict_type.upper()}"

        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            error_code=error_code,
            detail=detail,
        )


class DuplicateResourceException(ConflictException):
    """Raised when trying to create a duplicate resource."""

    def __init__(
        self,
        resource_type: str,
        field: str,
        value: Any,
    ):
        message = f"{resource_type} with {field} '{value}' already exists"
        detail = f"Another {resource_type.lower()} with this {field} already exists"

        super().__init__(
            message=message,
            conflict_type=f"{resource_type.upper()}_EXISTS",
            detail=detail,
        )
        self.error_code = f"DUPLICATE_{resource_type.upper()}"


class RateLimitException(AppException):
    """
    Raised when rate limit is exceeded.

    HTTP 429 Too Many Requests
    """

    def __init__(
        self,
        retry_after: Optional[int] = None,
        detail: Optional[str] = None,
    ):
        message = "Rate limit exceeded"
        if retry_after:
            message = f"Rate limit exceeded. Try again in {retry_after} seconds"

        headers = None
        if retry_after:
            headers = {"Retry-After": str(retry_after)}

        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            detail=detail,
            headers=headers,
        )


class ServerException(AppException):
    """
    Raised when an unexpected server error occurs.

    HTTP 500 Internal Server Error
    """

    def __init__(
        self,
        message: str = "Internal server error",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            error_code="INTERNAL_SERVER_ERROR",
            detail=detail,
        )


class DatabaseException(ServerException):
    """Raised when a database error occurs."""

    def __init__(
        self,
        message: str = "Database error",
        detail: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            detail=detail or "An error occurred while accessing the database",
        )
        self.error_code = "DATABASE_ERROR"


class FileProcessingException(AppException):
    """
    Raised when file processing fails.

    HTTP 422 Unprocessable Entity
    """

    def __init__(
        self,
        message: str = "File processing failed",
        filename: Optional[str] = None,
        detail: Optional[str] = None,
    ):
        if filename:
            message = f"Failed to process file '{filename}'"

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            error_code="FILE_PROCESSING_FAILED",
            detail=detail,
        )


class InvalidFileTypeException(FileProcessingException):
    """Raised when file type is not supported."""

    def __init__(
        self,
        filename: str,
        allowed_types: list[str],
    ):
        message = f"Invalid file type for '{filename}'"
        detail = f"Allowed file types: {', '.join(allowed_types)}"

        super().__init__(
            message=message,
            filename=filename,
            detail=detail,
        )
        self.error_code = "INVALID_FILE_TYPE"


class FileSizeLimitException(FileProcessingException):
    """Raised when file exceeds size limit."""

    def __init__(
        self,
        filename: str,
        max_size_mb: float,
    ):
        message = f"File '{filename}' exceeds size limit"
        detail = f"Maximum file size is {max_size_mb}MB"

        super().__init__(
            message=message,
            filename=filename,
            detail=detail,
        )
        self.error_code = "FILE_SIZE_LIMIT_EXCEEDED"


class ServiceUnavailableException(AppException):
    """
    Raised when a required service is unavailable.

    HTTP 503 Service Unavailable
    """

    def __init__(
        self,
        service_name: str,
        detail: Optional[str] = None,
    ):
        message = f"{service_name} is currently unavailable"
        if not detail:
            detail = f"The {service_name.lower()} service is temporarily unavailable. Please try again later."

        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            detail=detail,
        )
        self.error_code = f"{service_name.upper()}_UNAVAILABLE"


# Exception mapping for easy reference
EXCEPTION_MAP = {
    "validation": ValidationException,
    "authentication": AuthenticationException,
    "token_expired": TokenExpiredException,
    "invalid_token": InvalidTokenException,
    "authorization": AuthorizationException,
    "not_found": ResourceNotFoundException,
    "user_not_found": UserNotFoundException,
    "file_not_found": FileNotFoundException,
    "conflict": ConflictException,
    "duplicate": DuplicateResourceException,
    "rate_limit": RateLimitException,
    "server": ServerException,
    "database": DatabaseException,
    "file_processing": FileProcessingException,
    "invalid_file_type": InvalidFileTypeException,
    "file_size_limit": FileSizeLimitException,
    "service_unavailable": ServiceUnavailableException,
}
