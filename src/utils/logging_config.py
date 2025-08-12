"""
Logging configuration for the Enterprise Data Quality & Compliance Platform.

This module provides centralized logging configuration with structured logging,
log rotation, and different log levels for different environments.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    name: str = "enterprise_dq",
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Set up structured logging for the application.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        log_format: Log message format
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file is specified)
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (uses module name if not specified)

    Returns:
        Logger instance
    """
    if name is None:
        # Get the calling module's name
        import inspect

        frame = inspect.currentframe().f_back
        name = frame.f_globals.get("__name__", "enterprise_dq")

    return logging.getLogger(name)


# Environment-specific logging setup
def setup_environment_logging() -> logging.Logger:
    """
    Set up logging based on environment variables.

    Returns:
        Configured logger instance
    """
    env = os.getenv("ENV_NAME", "development")
    log_level = os.getenv("LOG_LEVEL", "INFO")

    if env == "production":
        log_file = "/var/log/enterprise_dq/app.log"
        return setup_logging(name="enterprise_dq", level=log_level, log_file=log_file)
    else:
        return setup_logging(name="enterprise_dq", level=log_level)


# Initialize default logger
_default_logger = setup_environment_logging()
