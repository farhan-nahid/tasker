"""
Logging Configuration Module.

This module provides centralized logging configuration using Loguru.
It sets up structured logging with custom formatting for both request
tracking and general application events.

Features:
- Colorized console output with structured format
- Request-specific logging with context (request_id, method, route, etc.)
- Application-level logging for startup, errors, and general events
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

Log Format:
    Request logs: timestamp | level | request_id | method | route | status | duration | ip | user_agent | message
    App logs: timestamp | level | message
"""

from loguru import logger
import sys
from enum import StrEnum
from typing import Literal


class LogLevels(StrEnum):
    """
    Enumeration of available logging levels.
    
    Provides type-safe logging level constants that match
    Python's standard logging levels.
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def configure_logging(log_level: str = LogLevels.INFO) -> None:
    """
    Configure Loguru with custom formatting for the application.
    
    Sets up two separate log handlers:
    1. Request logs: Full context with request details
    2. Application logs: Simple format for general events
    
    Args:
        log_level (str): Minimum log level to display (default: INFO)
        
    Example:
        configure_logging(LogLevels.DEBUG)
        logger.info("Application started")
        
        # For request logging:
        logger.bind(
            request_id="abc123",
            method="GET",
            route="/api/users",
            status=200,
            duration=45.2,
            ip="127.0.0.1",
            user_agent="Mozilla/5.0..."
        ).info("Request completed")
    """
    # Remove default Loguru handler
    logger.remove()

    # Format template for HTTP request logs
    # Includes all request context with color coding
    request_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
        "| <level>{level: <8}</level> "
        "| <blue>{extra[request_id]: <10}</blue> "
        "| <magenta>{extra[method]: <6}</magenta> "
        "| <cyan>{extra[route]: <25}</cyan> "
        "| <yellow>{extra[status]: <3}</yellow> "
        "| <white>{extra[duration]: >6}ms</white> "
        "| <green>{extra[ip]: <15}</green> "
        "| <dim>{extra[user_agent]}</dim> "
        "| {message}"
    )

    # Format template for general application logs
    # Simple format without request context
    simple_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
        "| <level>{level: <8}</level> "
        "| {message}"
    )

    # Handler for HTTP request logs
    # Only processes logs that include request_id in extra data
    logger.add(
        sys.stdout,
        level=log_level,
        format=request_format,
        filter=lambda record: "request_id" in record["extra"],
        colorize=True,
    )

    # Handler for general application logs  
    # Processes logs that don't include request context
    logger.add(
        sys.stdout,
        level=log_level,
        format=simple_format,
        filter=lambda record: "request_id" not in record["extra"],
        colorize=True,
    )

    logger.info("Logging configured successfully.")


# Export main components for external use
__all__ = ["logger", "configure_logging", "LogLevels"]
