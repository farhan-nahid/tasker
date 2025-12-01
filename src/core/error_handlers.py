from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Union
import traceback

from .errors import APIError, DatabaseError, ValidationError
from ..schemas.responses import APIResponse
from ..utils.logging import logger


def register_error_handlers(app) -> None:
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
    # Get request context from middleware
    request_id = getattr(request.state, 'request_id', 'unknown')
    client_ip = extract_client_ip(request)
    user_agent = request.headers.get("user-agent", "unknown")[:25]
    
    # Determine log level based on status code
    log_level = get_log_level(exc.status_code)
    
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
    # Extract client information
    client_ip = extract_client_ip(request)
    
    # Determine log level based on status code
    log_level = get_log_level(exc.status_code)[0]
    
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
    # Extract client information
    client_ip = extract_client_ip(request)
    
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
    # Extract client information
    client_ip = extract_client_ip(request)
    
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
    # Extract client information
    client_ip = extract_client_ip(request)
    
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


def extract_client_ip(request: Request) -> str:
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


def get_log_level(status_code: int) -> str:
    if status_code >= 500:
        return "error"
    elif status_code >= 400:
        return "warning"
    else:
        return "info"
