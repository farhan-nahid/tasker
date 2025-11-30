"""
Configuration Module Package.

This package contains all application configuration modules including:
- app_vars.py: Environment variables and application settings
- database.py: Database connection and session management

All configuration is centralized here to provide a single source
of truth for application settings and make environment-specific
configuration management easier.

Usage:
    from src.configs.app_vars import DATABASE_URL, PORT
    from src.configs.database import get_db, test_database_connection
"""

# Import main configuration items for easy access
from .app_vars import (
    DATABASE_URL,
    PORT,
    LOG_LEVEL,
    ENVIRONMENT
)
from .database import (
    get_db,
    test_database_connection,
    engine
)

__all__ = [
    "DATABASE_URL",
    "PORT", 
    "LOG_LEVEL",
    "ENVIRONMENT",
    "get_db",
    "test_database_connection",
    "engine"
]