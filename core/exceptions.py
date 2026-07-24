# core/exceptions.py
from typing import Any, Optional
from fastapi import status


class AppException(Exception):
    """
    Base exception class for all application domain errors.
    Carries an HTTP status code and detail message for central handling.
    """
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        payload: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.payload = payload
        super().__init__(self.message)


class DatabaseValidationError(AppException):
    """Raised when data fails database constraint or validation rules (400 Bad Request)."""
    def __init__(self, message: str, payload: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            payload=payload
        )


class ResourceNotFoundError(AppException):
    """Raised when a database record (Student, Template, Score) is missing (404 Not Found)."""
    def __init__(self, message: str = "The requested resource was not found."):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )


class ConflictError(AppException):
    """Raised when a unique resource constraint is violated, like a duplicate ID (409 Conflict)."""
    def __init__(self, message: str = "Resource already exists."):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )


class AuthenticationError(AppException):
    """Raised when JWT verification fails or credentials are invalid (401 Unauthorized)."""
    def __init__(self, message: str = "Could not validate credentials."):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class ForbiddenError(AppException):
    """Raised when an authenticated user lacks RBAC permissions (403 Forbidden)."""
    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )