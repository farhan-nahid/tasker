from loguru import logger
import sys
from enum import StrEnum


class LogLevels(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"  
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def configure_logging(log_level: str = LogLevels.INFO):
    """
    Configure Loguru for simple console logging with custom format.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Remove default logger
    logger.remove()
    
    # Add console logger with custom format
    # Format: timestamp | log_level | IP | method | route | response_time | message
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[ip]: <15}</cyan> | <magenta>{extra[method]: <6}</magenta> | <blue>{extra[route]: <20}</blue> | <yellow>{extra[response_time]: >6}ms</yellow> | {message}",
        filter=lambda record: "ip" in record["extra"],
        colorize=True
    )
    
    # Add simple logger for non-request logs (startup, database, etc.)
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        filter=lambda record: "ip" not in record["extra"],
        colorize=True
    )


# Export the configured logger for easy import
__all__ = ["logger", "configure_logging", "LogLevels"]