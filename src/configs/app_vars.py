"""
Application Configuration Variables.

This module loads and manages all environment variables used throughout
the application. It provides centralized configuration management with
sensible defaults for development environments.

Environment Variables:
    DB_HOST: Database host (default: localhost)
    DB_NAME: Database name (default: tasker)
    DB_USER: Database username (default: postgres)
    DB_PASSWORD: Database password (default: password)
    DB_PORT: Database port (default: 5432)
    PORT: Application server port (default: 8000)
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Database Configuration
DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_NAME: str = os.getenv("DB_NAME", "tasker")
DB_USER: str = os.getenv("DB_USER", "postgres")
DB_PASS: str = os.getenv("DB_PASSWORD", "password")
DB_PORT: int = int(os.getenv("DB_PORT", "5432"))

# Application Configuration
PORT: int = int(os.getenv("PORT", "8000"))

# Export all configuration variables
__all__ = [
    "DB_HOST",
    "DB_NAME", 
    "DB_USER",
    "DB_PASS",
    "DB_PORT",
    "PORT"
]