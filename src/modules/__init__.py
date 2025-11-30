"""
Modules Package.

This package contains all application modules organized by domain.
Each module follows a consistent structure with separate files for:

- models.py: Pydantic data models
- controllers.py: Business logic and data processing
- routes.py: FastAPI route definitions
- __init__.py: Module exports and configuration

Available Modules:
- health: Health monitoring and status endpoints

Usage:
    from src.modules.health import router as health_router
    app.include_router(health_router)
"""

# Import all module routers for easy access
from .health import router as health_router

__all__ = ["health_router"]