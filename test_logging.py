#!/usr/bin/env python3
"""
Test script to demonstrate Loguru logging usage.
"""

from src.logging import logger, configure_logging, LogLevels

def main():
    # Configure logging
    configure_logging(LogLevels.INFO)
    
    # Basic logging examples - just use logger.info(), logger.error(), etc.
    logger.info("Application started successfully")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # You can also add extra context using bind()
    logger.bind(ip="192.168.1.100", method="GET", route="/api/users", response_time=45.2).info("API request completed")
    
    logger.bind(ip="10.0.0.5", method="POST", route="/api/login", response_time=123.7).error("Authentication failed")
    
    # Simple logging without extra context
    logger.debug("Debug message (won't show unless level is DEBUG)")
    logger.info("Simple info message")

if __name__ == "__main__":
    main()