"""
Enterprise Data Quality Platform - ETL Pipelines Module

This module contains ETL (Extract, Transform, Load) pipelines for
processing and transforming enterprise data.
"""

from .contracts_etl_job import process_contracts_data
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

__version__ = "1.0.0"
__author__ = "Enterprise Data Platform Team"

__all__ = ["process_contracts_data"]
