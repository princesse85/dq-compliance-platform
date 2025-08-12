"""
Configuration module for Legal ML Pipeline.
"""

from .model_config import get_config, update_config, DEFAULT_CONFIG
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

__all__ = ['get_config', 'update_config', 'DEFAULT_CONFIG']
