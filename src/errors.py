"""
Custom Exception Classes for API Error Handling.

This module provides a comprehensive set of HTTP exception classes
that extend FastAPI's HTTPException with additional context and
standardized error formatting. Similar to Express.js error handling,
these exceptions can be raised anywhere and will be caught by
global error handlers.

Error Types:
- APIError: Base error class with automatic error code generation
- ValidationError: 422 - Request validation failures
- NotFoundError: 404 - Resource not found
- UnauthorizedError: 401 - Authentication required
- ForbiddenError: 403 - Access denied
- ConflictError: 409 - Resource conflicts
- RateLimitError: 429 - Rate limit exceeded
- DatabaseError: 500 - Database operation failures
- ExternalServiceError: 502 - External API failures
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from datetime import datetime


class APIError(HTTPException):
    """
    Base API error class with standardized formatting.
    
    Extends FastAPI's HTTPException to provide consistent error
    structure across the entire application. Automatically generates
    error codes and timestamps.
    
    Attributes:
        message (str): Human-readable error message
        error_code (str): Machine-readable error identifier
        details (dict): Additional error context data
        
    Example:
        # Basic usage
        raise APIError(
            message="Something went wrong",
            status_code=500
        )
        
        # With additional context
        raise APIError(
            message="Invalid user ID",
            status_code=400,
            error_code="INVALID_USER_ID", 
            details={"user_id": 123, "reason": "Not a valid format"}
        )
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize API error with message and optional context.
        
        Args:
            message (str): Human-readable error description
            status_code (int): HTTP status code (default: 500)
            error_code (str, optional): Machine-readable error code
            details (dict, optional): Additional error context
        """
        self.message = message
        self.error_code = error_code or self._generate_error_code(status_code)
        self.details = details or {}
        
        # Call parent HTTPException constructor
        super().__init__(status_code=status_code, detail=self.to_dict())
    
    def _generate_error_code(self, status_code: int) -> str:
        """
        Generate standardized error code from HTTP status code.
        
        Args:
            status_code (int): HTTP status code
            
        Returns:
            str: Machine-readable error code
        """
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
        """
        Convert error to standardized dictionary format.
        
        Returns:
            dict: Serializable error representation
        """
        return {
            "success": False,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "timestamp": datetime.utcnow().isoformat()
        }


# Specific error classes for common HTTP scenarios

class ValidationError(APIError):
    """
    Request validation error (HTTP 422).
    
    Used when request data fails validation (missing fields,
    invalid formats, constraint violations, etc.).
    
    Example:
        raise ValidationError(
            message="Email format is invalid",
            details={"field": "email", "value": "invalid-email"}
        )
    """
    
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
    """
    Resource not found error (HTTP 404).
    
    Used when a requested resource doesn't exist or
    user doesn't have permission to access it.
    
    Example:
        raise NotFoundError(
            message="User not found",
            resource="user"
        )
    """
    
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
    """
    Authentication required error (HTTP 401).
    
    Used when request requires valid authentication
    credentials that are missing or invalid.
    
    Example:
        raise UnauthorizedError(
            message="Invalid or expired token"
        )
    """
    
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
    """
    Access forbidden error (HTTP 403).
    
    Used when user is authenticated but doesn't have
    permission to access the requested resource.
    
    Example:
        raise ForbiddenError(
            message="Admin access required"
        )
    """
    
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
    """
    Resource conflict error (HTTP 409).
    
    Used when request conflicts with current resource state
    (e.g., duplicate email, concurrent modifications).
    
    Example:
        raise ConflictError(
            message="Email already exists"
        )
    """
    
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
    """
    Rate limit exceeded error (HTTP 429).
    
    Used when client has exceeded allowed request rate.
    Includes retry timing information.
    
    Example:
        raise RateLimitError(
            message="Too many requests",
            retry_after=60  # seconds
        )
    """
    
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
    """
    Database operation error (HTTP 500).
    
    Used when database operations fail (connection issues,
    constraint violations, transaction rollbacks, etc.).
    
    Example:
        raise DatabaseError(
            message="Failed to create user",
            operation="INSERT INTO users"
        )
    """
    
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
    """
    External service error (HTTP 502).
    
    Used when external API calls fail or return errors
    (payment gateways, email services, third-party APIs, etc.).
    
    Example:
        raise ExternalServiceError(
            message="Payment processing failed",
            service="stripe"
        )
    """
    
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


# Export all error classes for external use
__all__ = [
    "APIError",
    "ValidationError",
    "NotFoundError", 
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "RateLimitError",
    "DatabaseError",
    "ExternalServiceError"
]