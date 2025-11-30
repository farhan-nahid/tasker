"""
Health Module.

This module provides health monitoring and status endpoints
for the application. It includes health checks, system status,
and welcome information.

Components:
- models: Pydantic models for health-related responses
- controllers: Business logic for health operations
- routes: FastAPI route definitions
"""

from .routes import router

__all__ = ["router"]