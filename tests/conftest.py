"""
Pytest configuration and common fixtures for the Enterprise Data Quality Platform.
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch
from pathlib import Path


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="session")
def mock_aws_credentials():
    """Mock AWS credentials for testing."""
    with patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test-access-key',
        'AWS_SECRET_ACCESS_KEY': 'test-secret-key',
        'AWS_DEFAULT_REGION': 'us-east-1'
    }):
        yield


@pytest.fixture(scope="session")
def mock_s3_bucket():
    """Mock S3 bucket for testing."""
    return "test-enterprise-raw-dev-123456789012-us-east-1"


@pytest.fixture(scope="session")
def mock_environment():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'ENV_NAME': 'test',
        'PROJECT_PREFIX': 'enterprise',
        'AWS_REGION': 'us-east-1'
    }):
        yield


@pytest.fixture
def sample_contract_data():
    """Sample contract data for testing."""
    return {
        "contract_id": "CTR-001",
        "client_name": "Test Client",
        "contract_type": "Service Agreement",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "value": 100000,
        "status": "Active"
    }


@pytest.fixture
def sample_quality_metrics():
    """Sample data quality metrics for testing."""
    return {
        "completeness": 0.95,
        "accuracy": 0.92,
        "consistency": 0.88,
        "timeliness": 0.96,
        "validity": 0.94
    }


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture(scope="session")
def test_config():
    """Test configuration."""
    return {
        "project_prefix": "enterprise",
        "env_name": "test",
        "region": "us-east-1",
        "billing_email": "test@example.com",
        "monthly_budget": 1000
    }
