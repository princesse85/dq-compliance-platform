"""
Data generators module for Legal ML Pipeline.
"""

from .legal_text_generator import create_legal_text_generator, generate_enhanced_dataset
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

__all__ = ["create_legal_text_generator", "generate_enhanced_dataset"]
