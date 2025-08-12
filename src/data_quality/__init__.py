"""
Enterprise Data Quality Platform - Data Quality Module

This module provides comprehensive data quality assessment, validation,
and monitoring capabilities for enterprise data pipelines.
"""

from .quality_assessment import run as run_quality_assessment
from .data_validation_suite import build_validation_suite
from .generate_synthetic_data import generate_synthetic_data
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

__version__ = "1.0.0"
__author__ = "Enterprise Data Platform Team"

__all__ = ["run_quality_assessment", "build_validation_suite", "generate_synthetic_data"]
