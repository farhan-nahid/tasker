#!/usr/bin/env python3
"""
Main application entry point.

This module serves as the entry point for the Tasker FastAPI application.
It configures and starts the Uvicorn ASGI server with settings from environment variables.
"""

import uvicorn
from src.configs.app_vars import PORT


def main() -> None:
    """
    Start the FastAPI application server.
    
    Configures and runs the Uvicorn ASGI server with:
    - Host: 0.0.0.0 (accepts connections from any IP)
    - Port: Loaded from environment variable PORT (default: 8000)
    - Reload: Enabled for development (auto-restart on code changes)
    """
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=PORT,
        reload=True
    )


if __name__ == "__main__":
    main()
