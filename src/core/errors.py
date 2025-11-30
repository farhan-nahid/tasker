from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from datetime import datetime


class APIError(HTTPException):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.error_code = error_code or self._generate_error_code(status_code)
        self.details = details or {}
        
        # Call parent HTTPException constructor
        super().__init__(status_code=status_code, detail=self.to_dict())
    
    def _generate_error_code(self, status_code: int) -> str:
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
        return {
            "success": False,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "timestamp": datetime.utcnow().isoformat()
        }


# Specific error classes for common HTTP scenarios

class ValidationError(APIError):
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(APIError):
    def __init__(
        self,
        message: str = "Resource not found",
        resource: Optional[str] = None
    ) -> None:
        details = {"resource": resource} if resource else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details
        )


class UnauthorizedError(APIError):
    def __init__(
        self,
        message: str = "Unauthorized access"
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED"
        )


class ForbiddenError(APIError):
    def __init__(
        self,
        message: str = "Forbidden access"
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN"
        )


class ConflictError(APIError):
    def __init__(
        self,
        message: str = "Resource conflict"
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT"
        )


class RateLimitError(APIError):
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ) -> None:
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


class DatabaseError(APIError):
    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None
    ) -> None:
        details = {"operation": operation} if operation else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details
        )


class ExternalServiceError(APIError):
    def __init__(
        self,
        message: str = "External service error",
        service: Optional[str] = None
    ) -> None:
        details = {"service": service} if service else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details
        )

