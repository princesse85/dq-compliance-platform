"""
Production configuration for the Enterprise Data Quality & Compliance Platform.
"""

import os
from typing import Dict, Any


class ProductionConfig:
    """Production environment configuration."""
    
    # Environment
    ENV_NAME = "production"
    DEBUG = False
    TESTING = False
    
    # AWS Configuration
    AWS_REGION = os.getenv("AWS_REGION", "eu-west-2")
    AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")
    
    # Project Configuration
    PROJECT_PREFIX = os.getenv("PROJECT_PREFIX", "enterprise")
    
    # Billing and Cost Management
    BILLING_EMAIL = os.getenv("BILLING_EMAIL", "enterprise-support@company.com")
    MONTHLY_BUDGET = float(os.getenv("MONTHLY_BUDGET", "5000"))
    
    # Data Lake Configuration
    DATA_LAKE_BUCKETS = {
        "raw": f"{PROJECT_PREFIX}-raw-{ENV_NAME}-{AWS_ACCOUNT_ID}-{AWS_REGION}",
        "processed": f"{PROJECT_PREFIX}-processed-{ENV_NAME}-{AWS_ACCOUNT_ID}-{AWS_REGION}",
        "analytics": f"{PROJECT_PREFIX}-analytics-{ENV_NAME}-{AWS_ACCOUNT_ID}-{AWS_REGION}",
        "quality_logs": f"{PROJECT_PREFIX}-quality-logs-{ENV_NAME}-{AWS_ACCOUNT_ID}-{AWS_REGION}"
    }
    
    # Glue Configuration
    GLUE_DATABASE = f"{PROJECT_PREFIX}_{ENV_NAME}_data_catalog"
    GLUE_CRAWLER_ROLE = f"{PROJECT_PREFIX}-{ENV_NAME}-glue-crawler-role"
    GLUE_JOB_ROLE = f"{PROJECT_PREFIX}-{ENV_NAME}-glue-job-role"
    
    # Lambda Configuration
    LAMBDA_TIMEOUT = 900  # 15 minutes
    LAMBDA_MEMORY_SIZE = 1024
    LAMBDA_RUNTIME = "python3.9"
    
    # API Gateway Configuration
    API_GATEWAY_STAGE = "prod"
    API_GATEWAY_THROTTLE_RATE = 1000
    API_GATEWAY_THROTTLE_BURST = 500
    
    # Monitoring Configuration
    CLOUDWATCH_LOG_GROUP = f"/aws/enterprise-dq/{ENV_NAME}"
    CLOUDWATCH_RETENTION_DAYS = 30
    
    # Security Configuration
    ENCRYPTION_ALGORITHM = "AES256"
    KMS_KEY_ALIAS = f"{PROJECT_PREFIX}-{ENV_NAME}-key"
    
    # Data Quality Configuration
    QUALITY_THRESHOLD = 0.85
    QUALITY_CHECK_INTERVAL = 3600  # 1 hour
    
    # Machine Learning Configuration
    ML_MODEL_BUCKET = f"{PROJECT_PREFIX}-ml-models-{ENV_NAME}-{AWS_ACCOUNT_ID}-{AWS_REGION}"
    ML_ENDPOINT_NAME = f"{PROJECT_PREFIX}-{ENV_NAME}-ml-endpoint"
    ML_INSTANCE_TYPE = "ml.m5.large"
    ML_INSTANCE_COUNT = 2
    
    # Document Processing Configuration
    DOCUMENT_PROCESSING_BUCKET = f"{PROJECT_PREFIX}-documents-{ENV_NAME}-{AWS_ACCOUNT_ID}-{AWS_REGION}"
    TEXTTRACT_ROLE = f"{PROJECT_PREFIX}-{ENV_NAME}-textract-role"
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FILE = "/var/log/enterprise_dq/app.log"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Performance Configuration
    ETL_TIMEOUT = 7200  # 2 hours
    MAX_CONCURRENT_JOBS = 10
    
    # Compliance Configuration
    DATA_RETENTION_DAYS = 2555  # 7 years
    AUDIT_LOG_RETENTION_DAYS = 3650  # 10 years
    
    @classmethod
    def get_bucket_name(cls, bucket_type: str) -> str:
        """Get bucket name for the specified type."""
        return cls.DATA_LAKE_BUCKETS.get(bucket_type, "")
    
    @classmethod
    def get_glue_job_name(cls, job_type: str) -> str:
        """Get Glue job name for the specified type."""
        return f"{cls.PROJECT_PREFIX}-{cls.ENV_NAME}-{job_type}"
    
    @classmethod
    def get_lambda_function_name(cls, function_type: str) -> str:
        """Get Lambda function name for the specified type."""
        return f"{cls.PROJECT_PREFIX}-{cls.ENV_NAME}-{function_type}"
    
    @classmethod
    def get_stack_name(cls, stack_type: str) -> str:
        """Get CDK stack name for the specified type."""
        return f"{cls.PROJECT_PREFIX}-{stack_type}"
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }


# Export configuration instance
config = ProductionConfig()
