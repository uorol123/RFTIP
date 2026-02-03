"""
错误响应模式 - Error Response Schemas

Defines standard error response structures for consistent API error responses.
"""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed error information for validation errors."""

    field: Optional[str] = Field(None, description="Field name that caused the error")
    message: str = Field(..., description="Error message for the field")
    code: Optional[str] = Field(None, description="Specific error code for this field")


class ErrorResponse(BaseModel):
    """
    Standard error response format.

    All API errors should follow this structure for consistent client handling.
    """

    success: bool = Field(False, description="Always false for error responses")
    error_code: str = Field(..., description="Machine-readable error identifier")
    message: str = Field(..., description="Human-readable error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    errors: Optional[list[ErrorDetail]] = Field(
        None, description="List of validation errors (for validation errors)"
    )
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    path: Optional[str] = Field(None, description="Request path")
    timestamp: str = Field(..., description="Error timestamp (ISO 8601)")
    status_code: int = Field(..., description="HTTP status code", ge=400, le=599)

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "detail": "Please check your input",
                "errors": [
                    {
                        "field": "email",
                        "message": "Invalid email format",
                        "code": "INVALID_EMAIL"
                    }
                ],
                "request_id": "req_abc123",
                "path": "/api/auth/register",
                "timestamp": "2024-01-15T10:30:00Z",
                "status_code": 400
            }
        }


class ValidationErrorResponse(ErrorResponse):
    """Specialized error response for validation errors."""

    error_code: str = Field("VALIDATION_ERROR", description="Error code for validation")
    errors: list[ErrorDetail] = Field(
        ..., description="List of field-specific validation errors"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "errors": [
                    {
                        "field": "username",
                        "message": "Username must be at least 3 characters",
                        "code": "TOO_SHORT"
                    },
                    {
                        "field": "password",
                        "message": "Password must be at least 6 characters",
                        "code": "TOO_SHORT"
                    }
                ],
                "request_id": "req_def456",
                "path": "/api/auth/register",
                "timestamp": "2024-01-15T10:30:00Z",
                "status_code": 400
            }
        }


class AuthenticationErrorResponse(ErrorResponse):
    """Specialized error response for authentication errors."""

    error_code: str = Field(
        "AUTHENTICATION_FAILED", description="Error code for authentication failures"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "AUTHENTICATION_FAILED",
                "message": "Invalid username or password",
                "detail": "Please check your credentials and try again",
                "request_id": "req_ghi789",
                "path": "/api/auth/login",
                "timestamp": "2024-01-15T10:30:00Z",
                "status_code": 401
            }
        }


class AuthorizationErrorResponse(ErrorResponse):
    """Specialized error response for authorization errors."""

    error_code: str = Field(
        "PERMISSION_DENIED", description="Error code for authorization failures"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "PERMISSION_DENIED",
                "message": "You do not have permission to perform this action",
                "detail": "Required permission: files:delete",
                "request_id": "req_jkl012",
                "path": "/api/files/123",
                "timestamp": "2024-01-15T10:30:00Z",
                "status_code": 403
            }
        }


class NotFoundErrorResponse(ErrorResponse):
    """Specialized error response for not found errors."""

    error_code: str = Field("NOT_FOUND", description="Error code for missing resources")
    resource_type: Optional[str] = Field(None, description="Type of resource that was not found")
    resource_id: Optional[Any] = Field(None, description="ID of the missing resource")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "FILE_NOT_FOUND",
                "message": "File with ID 123 not found",
                "resource_type": "File",
                "resource_id": 123,
                "request_id": "req_mno345",
                "path": "/api/files/123",
                "timestamp": "2024-01-15T10:30:00Z",
                "status_code": 404
            }
        }


class ConflictErrorResponse(ErrorResponse):
    """Specialized error response for conflict errors."""

    error_code: str = Field("CONFLICT", description="Error code for conflicts")
    conflict_type: Optional[str] = Field(None, description="Type of conflict")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "DUPLICATE_USER",
                "message": "User with username 'john_doe' already exists",
                "conflict_type": "USERNAME_EXISTS",
                "request_id": "req_pqr678",
                "path": "/api/auth/register",
                "timestamp": "2024-01-15T10:30:00Z",
                "status_code": 409
            }
        }


class ServerErrorResponse(ErrorResponse):
    """Specialized error response for server errors."""

    error_code: str = Field(
        "INTERNAL_SERVER_ERROR", description="Error code for server errors"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "detail": "Please try again later or contact support if the problem persists",
                "request_id": "req_stu901",
                "path": "/api/files/upload",
                "timestamp": "2024-01-15T10:30:00Z",
                "status_code": 500
            }
        }


class SuccessResponse(BaseModel):
    """
    Standard success response wrapper.

    Wraps successful API responses with consistent structure.
    """

    success: bool = Field(True, description="Always true for success responses")
    message: Optional[str] = Field(None, description="Optional success message")
    data: Optional[Any] = Field(None, description="Response data")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    timestamp: str = Field(..., description="Response timestamp (ISO 8601)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": 123, "name": "Example"},
                "request_id": "req_vwx234",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


# Type alias for any error response type
AnyErrorResponse = (
    ErrorResponse
    | ValidationErrorResponse
    | AuthenticationErrorResponse
    | AuthorizationErrorResponse
    | NotFoundErrorResponse
    | ConflictErrorResponse
    | ServerErrorResponse
)
