from loguru import logger
import sys
from enum import StrEnum


class LogLevels(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def configure_logging(log_level: str = LogLevels.INFO) -> None:
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


