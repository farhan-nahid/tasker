from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import traceback

from .errors import APIError, DatabaseError, ValidationError
from .responses import APIResponse
from .logging import logger


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle custom API errors."""
    
    # Get request context
    request_id = getattr(request.state, 'request_id', 'unknown')
    client_ip = request.client.host if hasattr(request, 'client') and request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")[:25]
    
    # Log the error with context
    logger.bind(
        request_id=request_id,
        method=request.method,
        route=request.url.path,
        status=exc.status_code,
        duration=0,
        ip=client_ip,
        user_agent=user_agent
    ).error(f"API Error: {exc.message} (Code: {exc.error_code})")
    
    # Update request_id in error if available
    error_dict = exc.to_dict()
    if request_id:
        error_dict["request_id"] = request_id
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_dict
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    # Get client IP
    if hasattr(request, 'client') and request.client:
        client_ip = request.client.host
    else:
        client_ip = "unknown"
    
    logger.bind(
        ip=client_ip,
        method=request.method,
        route=request.url.path,
        response_time=0
    ).warning(f"HTTP Exception: {exc.detail} (Status: {exc.status_code})")
    
    # Create standardized error response
    error_response = APIResponse.error_response(message=str(exc.detail))
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    # Get client IP
    if hasattr(request, 'client') and request.client:
        client_ip = request.client.host
    else:
        client_ip = "unknown"
    
    # Format validation errors
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(x) for x in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    error_message = "Validation failed: " + "; ".join(errors)
    
    logger.bind(
        ip=client_ip,
        method=request.method,
        route=request.url.path,
        response_time=0
    ).warning(f"Validation Error: {error_message}")
    
    # Create validation error response
    validation_error = ValidationError(
        message="Request validation failed",
        details={"validation_errors": exc.errors()}
    )
    
    return JSONResponse(
        status_code=validation_error.status_code,
        content=validation_error.to_dict()
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors."""
    # Get client IP
    if hasattr(request, 'client') and request.client:
        client_ip = request.client.host
    else:
        client_ip = "unknown"
    
    # Log the database error
    logger.bind(
        ip=client_ip,
        method=request.method,
        route=request.url.path,
        response_time=0
    ).error(f"Database Error: {str(exc)}")
    
    # Create database error response
    db_error = DatabaseError(
        message="A database error occurred",
        operation="database_operation"
    )
    
    return JSONResponse(
        status_code=db_error.status_code,
        content=db_error.to_dict()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any unhandled exceptions."""
    # Get client IP
    if hasattr(request, 'client') and request.client:
        client_ip = request.client.host
    else:
        client_ip = "unknown"
    
    # Log the unexpected error with full traceback
    error_trace = traceback.format_exc()
    logger.bind(
        ip=client_ip,
        method=request.method,
        route=request.url.path,
        response_time=0
    ).error(f"Unhandled Exception: {str(exc)}\nTraceback: {error_trace}")
    
    # Create generic error response
    error_response = APIResponse.error_response(
        message="An unexpected error occurred",
        data={"error_type": type(exc).__name__}
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )