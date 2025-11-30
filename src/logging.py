from loguru import logger
import sys
from enum import StrEnum
from typing import Literal


class LogLevels(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def configure_logging(
    log_level: str = LogLevels.INFO,
):
    """
    Configure Loguru with simplified format:
    timestamp | level | request_id | method | route | status | duration | ip | user_agent | message
    """

    logger.remove()

    # Format for request logs
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

    # Format for simple logs
    simple_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
        "| <level>{level: <8}</level> "
        "| {message}"
    )

    # Console logging only
    # Request logs with full format
    logger.add(
        sys.stdout,
        level=log_level,
        format=request_format,
        filter=lambda record: "request_id" in record["extra"],
        colorize=True,
    )

    # Application logs with simplified format
    logger.add(
        sys.stdout,
        level=log_level,
        format=simple_format,
        filter=lambda record: "request_id" not in record["extra"],
        colorize=True,
    )

    logger.info("Logging configured successfully.")


__all__ = ["logger", "configure_logging", "LogLevels"]
