"""
FastAPI Application Entry Point.

This module creates and configures the main FastAPI application instance
with middleware, error handlers, CORS settings, and example routes.
It follows a modular architecture similar to Express.js applications.

Features:
- Professional logging middleware with structured output
- Comprehensive error handling with standardized responses
- Database connectivity with SQLAlchemy
- Example routes demonstrating response patterns
- Dependency injection for database sessions

Usage:
    This module is imported by main.py to run the application with uvicorn.
    The app instance can also be used for testing or deployment with
    other ASGI servers.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, Optional

# Import application modules
from .configs.database import get_db
from .logging import configure_logging, LogLevels, logger
from .responses import APIResponse, PaginatedResponse
from .errors import APIError, NotFoundError, ValidationError, DatabaseError
from .error_handlers import register_error_handlers
from .middlewares import logging_middleware
from .configs.app_vars import PORT


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Factory function that sets up the entire application with
    all necessary middleware, error handlers, and configuration.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    # Configure Loguru logging system
    configure_logging(LogLevels.INFO)
    logger.info(f"🚀 Initializing FastAPI application on port {PORT}")
    
    # Create FastAPI application instance with metadata
    app = FastAPI(
        title="Tasker API",
        description="A professional task management API built with FastAPI",
        version="1.0.0",
        docs_url="/docs",  # Swagger UI documentation
        redoc_url="/redoc",  # ReDoc documentation
        openapi_url="/openapi.json",
        dependencies=[Depends(get_db)]  # Global database dependency
    )
    
    # Configure CORS (Cross-Origin Resource Sharing) for web applications
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify actual origins
        allow_credentials=True,
        allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
        allow_headers=["*"],  # Accept all headers
    )
    
    # Register custom logging middleware (must be added after CORS)
    app.middleware("http")(logging_middleware)
    
    # Register global error handlers using centralized function
    register_error_handlers(app)
    
    logger.info("✅ FastAPI application configured successfully")
    return app


# Create the application instance
app = create_app()


@app.get("/", response_model=APIResponse[Dict[str, Any]])
async def read_root() -> APIResponse[Dict[str, Any]]:
    """
    Root endpoint providing API information.
    
    Returns:
        APIResponse[Dict]: Welcome message with API metadata
        
    Example Response:
        {
            "success": true,
            "data": {
                "version": "1.0.0",
                "status": "healthy",
                "documentation": "/docs"
            },
            "message": "Welcome to Tasker API"
        }
    """
    logger.info("Root endpoint accessed")
    
    return APIResponse.success_response(
        message="Welcome to Tasker API",
        data={
            "version": "1.0.0",
            "status": "healthy",
            "documentation": "/docs",
            "alternative_docs": "/redoc"
        }
    )


@app.get("/health", response_model=APIResponse[Dict[str, str]])
async def health_check() -> APIResponse[Dict[str, str]]:
    """
    Health check endpoint for monitoring and load balancers.
    
    Used by monitoring systems and load balancers to verify
    that the application is running and ready to serve requests.
    
    Returns:
        APIResponse[Dict]: Service health status
        
    Example Response:
        {
            "success": true,
            "data": {
                "status": "healthy",
                "uptime": "running"
            },
            "message": "Service is healthy"
        }
    """
    logger.info("Health check performed")
    
    return APIResponse.success_response(
        message="Service is healthy",
        data={
            "status": "healthy",
            "uptime": "running"
        }
    )


# Example endpoints demonstrating different error types and responses

@app.get("/test/not-found")
async def test_not_found() -> None:
    """
    Demonstration endpoint for 404 Not Found errors.
    
    Shows how custom NotFoundError exceptions are handled
    by the global error handlers and converted to standardized responses.
    
    Raises:
        NotFoundError: Always raises this exception for demonstration
    """
    logger.info("Testing NotFoundError handling")
    raise NotFoundError(
        message="Test resource not found",
        resource="test_item"
    )


@app.get("/test/validation-error")
async def test_validation_error() -> None:
    """
    Demonstration endpoint for 422 Validation errors.
    
    Shows how custom ValidationError exceptions are handled
    and provide detailed error information to clients.
    
    Raises:
        ValidationError: Always raises this exception for demonstration
    """
    logger.info("Testing ValidationError handling")
    raise ValidationError(
        message="Test validation failed",
        details={"field": "email", "error": "Invalid email format"}
    )


@app.get("/test/database-error")
async def test_database_error() -> None:
    """
    Demonstration endpoint for 500 Database errors.
    
    Shows how DatabaseError exceptions are handled when
    database operations fail.
    
    Raises:
        DatabaseError: Always raises this exception for demonstration
    """
    logger.info("Testing DatabaseError handling")
    raise DatabaseError(
        message="Test database operation failed",
        operation="SELECT * FROM test_table"
    )


@app.get("/test/generic-error")
async def test_generic_error() -> None:
    """
    Demonstration endpoint for unexpected errors.
    
    Shows how the catch-all exception handler processes
    unexpected exceptions and converts them to 500 responses.
    
    Raises:
        Exception: Always raises a generic exception for demonstration
    """
    logger.info("Testing generic exception handling")
    raise Exception("This is a test generic error")


@app.get("/test/paginated", response_model=PaginatedResponse[Dict[str, Any]])
async def test_paginated_response(
    page: int = 1, 
    per_page: int = 10
) -> PaginatedResponse[Dict[str, Any]]:
    """
    Demonstration endpoint for paginated responses.
    
    Shows how to use the PaginatedResponse class to return
    paginated data with metadata about the pagination state.
    
    Args:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 10)
        
    Returns:
        PaginatedResponse[Dict]: Paginated mock data with metadata
        
    Example Response:
        {
            "success": true,
            "data": [
                {"id": 1, "name": "Item 1", "description": "Description for item 1"},
                {"id": 2, "name": "Item 2", "description": "Description for item 2"}
            ],
            "message": "Paginated data retrieved successfully",
            "pagination": {
                "page": 1,
                "per_page": 10,
                "total": 100,
                "pages": 10,
                "has_next": true,
                "has_prev": false
            }
        }
    """
    logger.info(f"Testing paginated response: page={page}, per_page={per_page}")
    
    # Generate mock data (in real app, this would come from database)
    mock_data = [
        {
            "id": i,
            "name": f"Item {i}",
            "description": f"Description for item {i}"
        }
        for i in range(1, 101)  # 100 mock items
    ]
    
    # Simulate pagination logic
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_data = mock_data[start_index:end_index]
    
    logger.info(f"Returning {len(paginated_data)} items for page {page}")
    
    return PaginatedResponse.create(
        data=paginated_data,
        total=len(mock_data),
        page=page,
        per_page=per_page,
        message="Paginated data retrieved successfully"
    )


# Additional example endpoints for common API patterns

@app.get("/api/status", response_model=APIResponse[Dict[str, Any]])
async def get_api_status() -> APIResponse[Dict[str, Any]]:
    """
    Get detailed API status information.
    
    Provides comprehensive status information including
    configuration, environment, and operational metrics.
    
    Returns:
        APIResponse[Dict]: Detailed API status information
    """
    import datetime
    import os
    
    status_data = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python_version": os.sys.version,
        "port": PORT,
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "openapi": "/openapi.json"
        }
    }
    
    return APIResponse.success_response(
        message="API status retrieved successfully",
        data=status_data
    )


# Export the app instance for use in main.py
__all__ = ["app"]