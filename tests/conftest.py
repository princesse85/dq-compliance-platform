"""
Pytest configuration and common fixtures for the Enterprise Data Quality Platform.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from unittest.mock import Mock, patch
import boto3
from moto import mock_aws


@pytest.fixture
def sample_contracts_data():
    """Fixture providing sample contracts data for testing"""
    return pd.DataFrame({
        'contract_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
        'client_name': ['Client A', 'Client B', 'Client C', 'Client D', 'Client E'],
        'contract_value': [100000, 250000, 75000, 500000, 150000],
        'start_date': ['2024-01-01', '2024-02-15', '2024-03-01', '2024-01-15', '2024-02-01'],
        'end_date': ['2024-12-31', '2024-12-31', '2024-08-31', '2025-01-31', '2024-11-30'],
        'status': ['Active', 'Active', 'Pending', 'Active', 'Completed'],
        'contract_type': ['Service', 'Product', 'Service', 'Product', 'Service'],
        'risk_level': ['Low', 'Medium', 'Low', 'High', 'Medium'],
        'text_description': [
            'Excellent service contract with comprehensive coverage.',
            'Product delivery contract with quality assurance.',
            'Standard service agreement with basic terms.',
            'High-value product contract with premium features.',
            'Completed service contract with good performance.'
        ]
    })


@pytest.fixture
def sample_text_data():
    """Fixture providing sample text data for ML testing"""
    return pd.DataFrame({
        'text': [
            'This is a positive review about the product.',
            'I really enjoyed using this service.',
            'The quality is excellent and I recommend it.',
            'This is a negative review about the product.',
            'I did not like the service at all.',
            'The quality is poor and I do not recommend it.',
            'Amazing experience with the product.',
            'Terrible service, would not recommend.',
            'Great value for money.',
            'Disappointed with the quality.'
        ],
        'label': [1, 1, 1, 0, 0, 0, 1, 0, 1, 0]
    })


@pytest.fixture
def problematic_data():
    """Fixture providing data with quality issues for testing"""
    data = pd.DataFrame({
        'contract_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
        'client_name': ['Client A', '', 'Client C', 'Client D', 'Client E'],
        'contract_value': [-1000, 250000, 75000, 500000, 150000],
        'start_date': ['2024-01-01', 'invalid-date', '2024-03-01', '2024-01-15', '2024-02-01'],
        'end_date': ['2024-12-31', '2024-12-31', '2024-08-31', '2025-01-31', '2024-11-30'],
        'status': ['Active', 'Active', 'Pending', 'Active', 'Completed'],
        'contract_type': ['Service', 'Product', 'Service', 'Product', 'Service'],
        'risk_level': ['Low', 'Medium', 'Low', 'High', 'Medium']
    })
    return data


@pytest.fixture
def large_dataset():
    """Fixture providing larger dataset for performance testing"""
    np.random.seed(42)
    n_records = 1000
    
    return pd.DataFrame({
        'contract_id': [f'C{i:03d}' for i in range(1, n_records + 1)],
        'client_name': [f'Client {chr(65 + i % 26)}' for i in range(n_records)],
        'contract_value': np.random.randint(50000, 1000000, n_records),
        'start_date': pd.date_range('2024-01-01', periods=n_records, freq='D').strftime('%Y-%m-%d'),
        'end_date': pd.date_range('2024-12-31', periods=n_records, freq='D').strftime('%Y-%m-%d'),
        'status': np.random.choice(['Active', 'Pending', 'Completed'], n_records),
        'contract_type': np.random.choice(['Service', 'Product'], n_records),
        'risk_level': np.random.choice(['Low', 'Medium', 'High'], n_records)
    })


@pytest.fixture
def temp_dir():
    """Fixture providing temporary directory for file operations"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_aws_credentials():
    """Fixture to mock AWS credentials"""
    with patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SECURITY_TOKEN': 'testing',
        'AWS_SESSION_TOKEN': 'testing',
        'AWS_DEFAULT_REGION': 'us-east-1'
    }):
        yield


@pytest.fixture
def mock_s3_bucket(mock_aws_credentials):
    """Fixture providing mocked S3 bucket"""
    with mock_aws():
        s3_client = boto3.client('s3', region_name='us-east-1')
        bucket_name = 'test-data-quality-bucket'
        s3_client.create_bucket(Bucket=bucket_name)
        yield s3_client, bucket_name


@pytest.fixture
def mock_lambda_function(mock_aws_credentials):
    """Fixture providing mocked Lambda function"""
    with mock_aws():
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        yield lambda_client


@pytest.fixture
def mock_sqs_queue(mock_aws_credentials):
    """Fixture providing mocked SQS queue"""
    with mock_aws():
        sqs_client = boto3.client('sqs', region_name='us-east-1')
        queue_name = 'test-data-quality-queue'
        response = sqs_client.create_queue(QueueName=queue_name)
        queue_url = response['QueueUrl']
        yield sqs_client, queue_url


@pytest.fixture
def mock_sns_topic(mock_aws_credentials):
    """Fixture providing mocked SNS topic"""
    with mock_aws():
        sns_client = boto3.client('sns', region_name='us-east-1')
        topic_name = 'test-data-quality-topic'
        response = sns_client.create_topic(Name=topic_name)
        topic_arn = response['TopicArn']
        yield sns_client, topic_arn


@pytest.fixture
def mock_cloudwatch_client(mock_aws_credentials):
    """Fixture providing mocked CloudWatch client"""
    with mock_aws():
        cloudwatch_client = boto3.client('cloudwatch', region_name='us-east-1')
        yield cloudwatch_client


@pytest.fixture
def quality_assessment_instance():
    """Fixture providing DataQualityAssessment instance"""
    from src.data_quality.quality_assessment import DataQualityAssessment
    return DataQualityAssessment()


@pytest.fixture
def validation_suite_instance():
    """Fixture providing DataValidationSuite instance"""
    from src.data_quality.data_validation_suite import DataValidationSuite
    return DataValidationSuite()


@pytest.fixture
def etl_job_instance():
    """Fixture providing ContractsETLJob instance"""
    from src.etl_pipelines.contracts_etl_job import ContractsETLJob
    return ContractsETLJob()


@pytest.fixture
def ml_baseline_instance():
    """Fixture providing TFIDFBaseline instance"""
    from src.ml.baseline_tf_idf import TFIDFBaseline
    return TFIDFBaseline()


@pytest.fixture
def evaluation_report_instance():
    """Fixture providing EvaluationReport instance"""
    from src.ml.eval_report import EvaluationReport
    return EvaluationReport()


@pytest.fixture
def expected_schema():
    """Fixture providing expected data schema"""
    return {
        'contract_id': 'object',
        'client_name': 'object',
        'contract_value': 'int64',
        'start_date': 'object',
        'end_date': 'object',
        'status': 'object',
        'contract_type': 'object',
        'risk_level': 'object'
    }


@pytest.fixture
def business_rules():
    """Fixture providing business rules for validation"""
    return {
        'contract_value_positive': lambda df: df['contract_value'] > 0,
        'start_date_before_end_date': lambda df: pd.to_datetime(df['start_date']) < pd.to_datetime(df['end_date']),
        'valid_status': lambda df: df['status'].isin(['Active', 'Pending', 'Completed', 'Terminated']),
        'valid_risk_level': lambda df: df['risk_level'].isin(['Low', 'Medium', 'High'])
    }


@pytest.fixture
def test_metrics():
    """Fixture providing test metrics for ML evaluation"""
    return {
        'accuracy': 0.85,
        'precision': 0.82,
        'recall': 0.88,
        'f1': 0.85,
        'roc_auc': 0.92
    }


@pytest.fixture
def test_parameters():
    """Fixture providing test parameters for ML training"""
    return {
        'learning_rate': 0.001,
        'batch_size': 32,
        'epochs': 10,
        'max_length': 512,
        'model_name': 'bert-base-uncased'
    }


@pytest.fixture
def mock_transformer_trainer():
    """Fixture providing mocked TransformerTrainer"""
    with patch('src.ml.transformer_train.AutoTokenizer.from_pretrained') as mock_tokenizer, \
         patch('src.ml.transformer_train.AutoModelForSequenceClassification.from_pretrained') as mock_model, \
         patch('src.ml.transformer_train.Trainer') as mock_trainer_class:
        
        mock_tokenizer.return_value = Mock()
        mock_model.return_value = Mock()
        mock_trainer = Mock()
        mock_trainer_class.return_value = mock_trainer
        
        from src.ml.transformer_train import TransformerTrainer
        trainer = TransformerTrainer()
        
        yield trainer, mock_tokenizer, mock_model, mock_trainer


@pytest.fixture
def mock_mlflow():
    """Fixture providing mocked MLflow"""
    with patch('src.ml.mlflow_utils.mlflow') as mock_mlflow:
        yield mock_mlflow


@pytest.fixture
def performance_thresholds():
    """Fixture providing performance thresholds for testing"""
    return {
        'min_accuracy': 0.7,
        'min_precision': 0.6,
        'min_recall': 0.6,
        'max_processing_time': 300,  # seconds
        'max_memory_usage': 1024,  # MB
        'min_quality_score': 0.8
    }


@pytest.fixture
def test_config():
    """Fixture providing test configuration"""
    return {
        'environment': 'test',
        'region': 'us-east-1',
        'project_prefix': 'test',
        'billing_email': 'test@example.com',
        'monthly_budget': 1000,
        'log_level': 'INFO',
        'enable_monitoring': True,
        'enable_alerting': True
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "aws: mark test as requiring AWS services"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location"""
    for item in items:
        # Add unit marker for tests in unit directory
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker for tests in integration directory
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add AWS marker for AWS integration tests
        if "aws_integration" in item.nodeid:
            item.add_marker(pytest.mark.aws)
        
        # Add slow marker for end-to-end tests
        if "end_to_end" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # Add performance marker for performance tests
        if "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
