"""
Logging configuration for the Enterprise Data Quality & Compliance Platform.

This module provides centralized logging configuration with structured logging,
log rotation, and different log levels for different environments.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(
    name: str = "enterprise_dq",
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
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
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
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
from src.utils.logging_config import get_logger

logger = get_logger(__name__)
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'enterprise_dq')
    
    return logging.getLogger(name)


# Environment-specific logging setup
def setup_environment_logging() -> logging.Logger:
    """
    Set up logging based on the current environment.
    
    Returns:
        Configured logger for the current environment
    """
    env = os.getenv("ENV_NAME", "development").lower()
    
    if env == "production":
        # Production: INFO level, file logging
        log_file = "/var/log/enterprise_dq/app.log"
        level = "INFO"
    elif env == "staging":
        # Staging: DEBUG level, file logging
        log_file = "logs/staging.log"
        level = "DEBUG"
    else:
        # Development: DEBUG level, console only
        log_file = None
        level = "DEBUG"
    
    return setup_logging(
        name="enterprise_dq",
        level=level,
        log_file=log_file
    )


# Structured logging helpers
class StructuredLogger:
    """Helper class for structured logging with context."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_operation_start(self, operation: str, **kwargs):
        """Log the start of an operation."""
        self.logger.info(f"Starting operation: {operation}", extra={
            'operation': operation,
            'status': 'started',
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        })
    
    def log_operation_success(self, operation: str, **kwargs):
        """Log successful completion of an operation."""
        self.logger.info(f"Operation completed successfully: {operation}", extra={
            'operation': operation,
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        })
    
    def log_operation_error(self, operation: str, error: Exception, **kwargs):
        """Log an operation error."""
        self.logger.error(f"Operation failed: {operation} - {str(error)}", extra={
            'operation': operation,
            'status': 'failed',
            'error': str(error),
            'error_type': type(error).__name__,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        })
    
    def log_data_quality_metric(self, metric_name: str, value: float, **kwargs):
        """Log a data quality metric."""
        self.logger.info(f"Data quality metric: {metric_name} = {value}", extra={
            'metric_name': metric_name,
            'metric_value': value,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        })
    
    def log_model_performance(self, model_name: str, metric: str, value: float, **kwargs):
        """Log model performance metrics."""
        self.logger.info(f"Model performance: {model_name} - {metric} = {value}", extra={
            'model_name': model_name,
            'metric': metric,
            'value': value,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        })


# Initialize default logger
default_logger = setup_environment_logging()
structured_logger = StructuredLogger(default_logger)
