"""Common utilities for document processing Lambda functions."""

import json
import os
import logging
from datetime import datetime
import boto3

# Configure logging
log = logging.getLogger()
log.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')

# Environment variables
RAW_BUCKET = os.environ.get('RAW_BUCKET')
PROCESSED_BUCKET = os.environ.get('PROCESSED_BUCKET')
ANALYTICS_BUCKET = os.environ.get('ANALYTICS_BUCKET')
LOW_CONF_THRESHOLD = float(os.environ.get('LOW_CONF_THRESHOLD', '0.85'))

def write_s3_text(bucket: str, key: str, text: str) -> None:
    """Write text content to S3 bucket."""
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=text.encode('utf-8'),
            ContentType='text/plain'
        )
        log.info(f"Successfully wrote text to s3://{bucket}/{key}")
    except Exception as e:
        log.error(f"Failed to write text to s3://{bucket}/{key}: {str(e)}")
        raise

def write_s3_json(bucket: str, key: str, data: dict) -> None:
    """Write JSON data to S3 bucket."""
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data, indent=2),
            ContentType='application/json'
        )
        log.info(f"Successfully wrote JSON to s3://{bucket}/{key}")
    except Exception as e:
        log.error(f"Failed to write JSON to s3://{bucket}/{key}: {str(e)}")
        raise

def get_current_date() -> str:
    """Get current date in YYYY-MM-DD format."""
    return datetime.utcnow().strftime('%Y-%m-%d')

def validate_environment() -> bool:
    """Validate that required environment variables are set."""
    required_vars = ['RAW_BUCKET', 'PROCESSED_BUCKET', 'ANALYTICS_BUCKET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        log.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    return True
