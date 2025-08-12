"""
Enterprise Data Quality Platform - Machine Learning Module

This module provides machine learning capabilities for data quality
assessment, risk prediction, and automated compliance monitoring.
"""

from .mlflow_utils import init_mlflow
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

__version__ = "1.0.0"
__author__ = "Enterprise Data Platform Team"

__all__ = ["init_mlflow"]
