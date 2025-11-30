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

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Import application modules
from .configs.database import get_db
from .logging import configure_logging, LogLevels, logger
from .responses import APIResponse
from .error_handlers import register_error_handlers
from .middlewares.logging_middleware import logging_middleware
from .configs.app_vars import PORT


def create_app() -> FastAPI:
    configure_logging(LogLevels.INFO)
    logger.info(f"🚀 Initializing application on http://localhost:{PORT}")
    
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


@app.get("/", response_model=APIResponse)
async def read_root() -> APIResponse:
    """Root endpoint providing API information."""
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


@app.get("/health", response_model=APIResponse)
async def health_check() -> APIResponse:
    """Health check endpoint for monitoring."""
    logger.info("Health check performed")
    
    return APIResponse.success_response(
        message="Service is healthy",
        data={
            "status": "healthy",
            "uptime": "running"
        }
    )