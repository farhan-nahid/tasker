"""
Global Error Handlers for FastAPI Application.

This module provides centralized error handling for all uncaught exceptions
across the application. Similar to Express.js error middleware, these handlers
catch exceptions thrown from any route or middleware and convert them to
standardized JSON responses.

Error Handler Types:
1. APIError Handler: Handles custom application errors with structured format
2. HTTP Exception Handler: Generic FastAPI HTTP exceptions
3. Validation Handler: FastAPI request validation errors (422)
4. Database Handler: SQLAlchemy database operation errors
5. General Exception Handler: Catch-all for unexpected errors

All handlers log errors appropriately and return consistent JSON responses
using the standardized APIResponse format.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Union
import traceback

from .errors import APIError, DatabaseError, ValidationError
from .responses import APIResponse
from .logging import logger


def register_error_handlers(app) -> None:
    """
    Register all error handlers with the FastAPI application.
    
    This function should be called during app initialization to set up
    global error handling. It registers handlers in order of specificity,
    with the most general handler last.
    
    Args:
        app: FastAPI application instance
        
    Example:
        app = FastAPI()
        register_error_handlers(app)
    """
    # Register custom API error handler (most specific)
    app.exception_handler(APIError)(api_error_handler)
    
    # Register FastAPI HTTP exception handler
    app.exception_handler(HTTPException)(http_exception_handler)
    
    # Register FastAPI validation error handler
    app.exception_handler(RequestValidationError)(validation_exception_handler)
    
    # Register database error handler
    app.exception_handler(SQLAlchemyError)(database_exception_handler)
    
    # Register catch-all exception handler (most general)
    app.exception_handler(Exception)(generic_exception_handler)


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """
    Handle custom APIError exceptions.
    
    Processes application-specific errors that inherit from APIError.
    These errors already contain proper formatting and status codes,
    so they're logged and returned as-is.
    
    Args:
        request (Request): FastAPI request object
        exc (APIError): Custom API error instance
        
    Returns:
        JSONResponse: Formatted error response with request context
        
    Example Response:
        {
            "success": false,
            "message": "User not found",
            "error_code": "NOT_FOUND", 
            "details": {"user_id": 123},
            "timestamp": "2025-11-30T20:15:32.123Z",
            "request_id": "abc12345"
        }
    """
    # Get request context from middleware
    request_id = getattr(request.state, 'request_id', 'unknown')
    client_ip = _extract_client_ip(request)
    user_agent = request.headers.get("user-agent", "unknown")[:25]
    
    # Determine log level based on status code
    log_level = _get_log_level(exc.status_code)
    
    # Log the error with full context using structured logging
    logger.bind(
        request_id=request_id,
        method=request.method,
        route=request.url.path,
        status=exc.status_code,
        duration=0,  # Duration not available in error handler
        ip=client_ip,
        user_agent=user_agent,
        error_code=exc.error_code
    ).__getattribute__(log_level)(f"API Error: {exc.message}")
    
    # Add request ID to error response for correlation
    error_dict = exc.to_dict()
    if request_id != 'unknown':
        error_dict["request_id"] = request_id
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_dict
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle generic FastAPI HTTP exceptions.
    
    Catches standard HTTP exceptions that aren't custom APIErrors.
    This includes built-in FastAPI errors and manually raised HTTPExceptions.
    
    Args:
        request (Request): FastAPI request object
        exc (HTTPException): Standard HTTP exception
        
    Returns:
        JSONResponse: Formatted HTTP error response
        
    Example Response:
        {
            "success": false,
            "message": "Method not allowed",
            "data": null
        }
    """
    # Extract client information
    client_ip = _extract_client_ip(request)
    
    # Determine log level based on status code
    log_level = _get_log_level(exc.status_code)
    
    # Log the HTTP error with context
    logger.bind(
        ip=client_ip,
        method=request.method,
        route=request.url.path,
        status=exc.status_code,
        response_time=0
    ).__getattribute__(log_level)(f"HTTP Exception: {exc.detail}")
    
    # Create standardized error response
    error_response = APIResponse.error_response(message=str(exc.detail))
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle FastAPI request validation errors (HTTP 422).
    
    Processes errors when request data doesn't match expected schema
    (missing fields, wrong types, validation constraints, etc.).
    Formats validation errors into user-friendly messages.
    
    Args:
        request (Request): FastAPI request object
        exc (RequestValidationError): FastAPI validation error
        
    Returns:
        JSONResponse: Formatted validation error response
        
    Example Response:
        {
            "success": false,
            "message": "Request validation failed",
            "error_code": "VALIDATION_ERROR",
            "details": {
                "validation_errors": [
                    {"loc": ["body", "email"], "msg": "Invalid email format", "type": "value_error.email"}
                ]
            },
            "timestamp": "2025-11-30T20:15:32.123Z"
        }
    """
    # Extract client information
    client_ip = _extract_client_ip(request)
    
    # Format validation errors for better readability
    formatted_errors = []
    for error in exc.errors():
        field = " -> ".join(str(x) for x in error["loc"][1:])  # Skip 'body'
        message = error["msg"]
        formatted_errors.append(f"{field}: {message}")
    
    error_summary = "Validation failed: " + "; ".join(formatted_errors)
    
    # Log the validation error
    logger.bind(
        ip=client_ip,
        method=request.method,
        route=request.url.path,
        status=422,
        response_time=0,
        validation_errors=exc.errors()
    ).warning(f"Validation Error: {error_summary}")
    
    # Create validation error response with detailed error information
    validation_error = ValidationError(
        message="Request validation failed",
        details={"validation_errors": exc.errors()}
    )
    
    return JSONResponse(
        status_code=validation_error.status_code,
        content=validation_error.to_dict()
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle SQLAlchemy database operation errors.
    
    Catches database-related errors like connection failures,
    constraint violations, transaction rollbacks, etc.
    Prevents exposing sensitive database details to clients.
    
    Args:
        request (Request): FastAPI request object
        exc (SQLAlchemyError): SQLAlchemy database error
        
    Returns:
        JSONResponse: Generic database error response
        
    Example Response:
        {
            "success": false,
            "message": "A database error occurred",
            "error_code": "DATABASE_ERROR",
            "details": {"operation": "database_operation"},
            "timestamp": "2025-11-30T20:15:32.123Z"
        }
    """
    # Extract client information
    client_ip = _extract_client_ip(request)
    
    # Log the database error with full details (for internal debugging)
    logger.bind(
        ip=client_ip,
        method=request.method,
        route=request.url.path,
        status=500,
        response_time=0,
        exception_type=type(exc).__name__,
        exception_message=str(exc)
    ).error(f"Database Error: {str(exc)}")
    
    # Create generic database error response (don't expose internal details)
    db_error = DatabaseError(
        message="A database error occurred",
        operation="database_operation"
    )
    
    return JSONResponse(
        status_code=db_error.status_code,
        content=db_error.to_dict()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all uncaught exceptions (catch-all handler).
    
    This is the last resort handler for any exceptions that weren't
    caught by more specific handlers. It prevents application crashes
    and ensures consistent error responses.
    
    Args:
        request (Request): FastAPI request object
        exc (Exception): Any uncaught exception
        
    Returns:
        JSONResponse: Generic internal server error response
        
    Example Response:
        {
            "success": false,
            "message": "An unexpected error occurred",
            "data": {"error_type": "ValueError"}
        }
    """
    # Extract client information
    client_ip = _extract_client_ip(request)
    
    # Log the unexpected error with full traceback for debugging
    error_trace = traceback.format_exc()
    logger.bind(
        ip=client_ip,
        method=request.method,
        route=request.url.path,
        status=500,
        response_time=0,
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        traceback=error_trace
    ).error(f"Unhandled Exception: {type(exc).__name__}: {str(exc)}")
    
    # Create generic error response (don't expose internal details)
    error_response = APIResponse.error_response(
        message="An unexpected error occurred",
        data={"error_type": type(exc).__name__}
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


def _extract_client_ip(request: Request) -> str:
    """
    Extract client IP address with proxy header support.
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        str: Client IP address or "unknown" if not found
    """
    if hasattr(request, 'client') and request.client:
        return request.client.host
    
    # Check proxy headers
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    return "unknown"


def _get_log_level(status_code: int) -> str:
    """
    Determine appropriate log level for HTTP status code.
    
    Args:
        status_code (int): HTTP response status code
        
    Returns:
        str: Log level ("info", "warning", or "error")
    """
    if status_code >= 500:
        return "error"
    elif status_code >= 400:
        return "warning"
    else:
        return "info"


# Export registration function for external use
__all__ = ["register_error_handlers"]