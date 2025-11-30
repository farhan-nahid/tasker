from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from datetime import datetime


class APIError(HTTPException):
    """Base API error class similar to Express.js error handling."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self._generate_error_code(status_code)
        self.details = details or {}
        
        super().__init__(status_code=status_code, detail=self.to_dict())
    
    def _generate_error_code(self, status_code: int) -> str:
        """Generate error code based on status code."""
        error_codes = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_SERVER_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE"
        }
        return error_codes.get(status_code, "UNKNOWN_ERROR")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "success": False,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


# Specific error classes for common scenarios
class ValidationError(APIError):
    """Validation error (422)."""
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(APIError):
    """Resource not found error (404)."""
    def __init__(
        self,
        message: str = "Resource not found",
        resource: Optional[str] = None
    ):
        details = {"resource": resource} if resource else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details
        )


class UnauthorizedError(APIError):
    """Unauthorized error (401)."""
    def __init__(
        self,
        message: str = "Unauthorized access"
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED"
        )


class ForbiddenError(APIError):
    """Forbidden error (403)."""
    def __init__(
        self,
        message: str = "Forbidden access"
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN"
        )


class ConflictError(APIError):
    """Conflict error (409)."""
    def __init__(
        self,
        message: str = "Resource conflict"
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT"
        )


class RateLimitError(APIError):
    """Rate limit exceeded error (429)."""
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


class DatabaseError(APIError):
    """Database operation error (500)."""
    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None
    ):
        details = {"operation": operation} if operation else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details
        )


class ExternalServiceError(APIError):
    """External service error (502)."""
    def __init__(
        self,
        message: str = "External service error",
        service: Optional[str] = None
    ):
        details = {"service": service} if service else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details
        )