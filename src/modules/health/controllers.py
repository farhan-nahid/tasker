import datetime
import os
import sys

from .models import WelcomeData, HealthData, StatusData
from ...configs.app_vars import PORT, ENVIRONMENT


def get_welcome_info() -> WelcomeData:
    return WelcomeData(
        version="1.0.0",
        status="healthy",
        documentation="/docs",
        alternative_docs="/redoc"
    )


def get_health_status() -> HealthData:
    return HealthData(
        status="healthy",
        uptime="running"
    )


def get_system_status() -> StatusData:
    return StatusData(
        timestamp=datetime.datetime.utcnow().isoformat(),
        environment=ENVIRONMENT,
        python_version=sys.version,
        port=PORT,
        endpoints={
            "docs": "/docs",
            "redoc": "/redoc", 
            "health": "/health",
            "status": "/status",
            "openapi": "/openapi.json"
        }
    )
