import datetime
import sys

from .models import WelcomeData, HealthData, StatusData, DBCheckData
from ...configs.app_vars import PORT, ENVIRONMENT
from ...configs.database import check_db_connection


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

    """Perform a real database connectivity check using the project's
    `check_db_connection` helper. On success return connected status and
    round-trip time in milliseconds; on failure return disconnected and the
    error message.
    """
    try:
        import time

        start = time.time()
        # check_db_connection will raise on failure
        check_db_connection()
        duration_ms = round((time.time() - start) * 1000, 1)

        return DBCheckData(
            database="connected",
            message=f"Database connection successful ({duration_ms}ms)"
        )

    except Exception as e:
        # Return the error message but avoid exposing sensitive details in
        # production. The raw exception is useful for local/dev debugging.
        return DBCheckData(
            database="disconnected",
            message=str(e)
        )