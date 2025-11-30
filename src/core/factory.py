from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from ..configs.database import get_db
from ..utils.logging import configure_logging, LogLevels, logger
from .error_handlers import register_error_handlers
from ..middlewares.logging_middleware import logging_middleware
from ..configs.app_vars import PORT


def create_app() -> FastAPI:
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
