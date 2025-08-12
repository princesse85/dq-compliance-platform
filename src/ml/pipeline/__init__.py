"""
Pipeline module for Legal ML Pipeline.
"""

from .legal_ml_pipeline import LegalMLPipeline
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

__all__ = ["LegalMLPipeline"]
