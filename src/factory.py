"""
FastAPI Application Factory.

This module contains the application factory function that creates
and configures the FastAPI application instance with all necessary
middleware, error handlers, and settings.

The factory pattern allows for better testing and configuration
management by keeping the app creation logic separate from
the route definitions.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .configs.database import get_db
from .logging import configure_logging, LogLevels, logger
from .error_handlers import register_error_handlers
from .middlewares.logging_middleware import logging_middleware
from .configs.app_vars import PORT


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Factory function that sets up the entire application with
    all necessary middleware, error handlers, and configuration.
    
    Returns:
        FastAPI: Configured FastAPI application instance
        
    Example:
        app = create_app()
        # App is ready to use with all middleware and handlers configured
    """
    # Configure logging system
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


# Export the factory function
__all__ = ["create_app"]