from fastapi import FastAPI, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from .configs.database import get_db
from .logging import configure_logging, LogLevels, logger
from .responses import APIResponse, PaginatedResponse
from .errors import APIError, NotFoundError, ValidationError, DatabaseError
from .error_handlers import (
    api_error_handler,
    http_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    generic_exception_handler
)
from .middlewares import logging_middleware
from src.configs.app_vars import PORT


# Configure Loguru logging
configure_logging(LogLevels.INFO)

# Log application startup
logger.info(f"Server starting on http://localhost:{PORT}")

app = FastAPI(
    title="Tasker API",
    description="Professional Task Management API",
    version="1.0.0",
    dependencies=[Depends(get_db)]
)

# Register error handlers (similar to Express.js error middleware)
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Register logging middleware
app.middleware("http")(logging_middleware)

@app.get("/", response_model=APIResponse)
async def read_root():
    return APIResponse.success_response(
        message="Welcome to Tasker API",
        data={
            "version": "1.0.0",
            "status": "healthy",
        },
    )


@app.get("/health", response_model=APIResponse)
async def health_check():
    return APIResponse.success_response(
        message="Service is healthy",
        data={
            "status": "healthy",
            "uptime": "running"
        },
    )


# Example endpoints demonstrating error handling
@app.get("/test/not-found")
async def test_not_found():
    raise NotFoundError(
        message="Test resource not found",
        resource="test_item"
    )


@app.get("/test/validation-error")
async def test_validation_error():
    raise ValidationError(
        message="Test validation failed",
        details={"field": "email", "error": "Invalid email format"}
    )


@app.get("/test/database-error")
async def test_database_error():
    raise DatabaseError(
        message="Test database operation failed",
        operation="SELECT * FROM test_table"
    )


@app.get("/test/generic-error")
async def test_generic_error():
    raise Exception("This is a test generic error")


@app.get("/test/paginated", response_model=PaginatedResponse)
async def test_paginated_response(page: int = 1, per_page: int = 10):
    mock_data = [
        {"id": i, "name": f"Item {i}", "description": f"Description for item {i}"}
        for i in range(1, 101)
    ]
    
    # Simulate pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = mock_data[start:end]
    
    return PaginatedResponse.create(
        data=paginated_data,
        total=len(mock_data),
        page=page,
        per_page=per_page,
        message="Paginated data retrieved successfully"
    )