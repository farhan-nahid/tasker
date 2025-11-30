"""
Middleware Package.

This package contains all custom middleware for the FastAPI application.
Middleware functions process requests and responses globally across
all routes, similar to Express.js middleware.

Available Middleware:
- logging_middleware: HTTP request/response logging with structured format

Middleware Order:
1. CORS (FastAPI built-in)
2. Logging middleware (custom)
3. Route handlers
4. Error handlers

Usage:
    from src.middlewares import logging_middleware
    app.middleware("http")(logging_middleware)
"""

from .logging_middleware import logging_middleware

__all__ = ["logging_middleware"]