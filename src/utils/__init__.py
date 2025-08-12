"""
Utility modules for the Enterprise Data Quality & Compliance Platform.
"""

from .logging_config import setup_logging, get_logger

logger = get_logger(__name__)

__all__ = ["setup_logging", "get_logger"]
