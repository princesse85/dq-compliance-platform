"""Common utilities for document processing Lambda functions."""

import json
import os
from datetime import datetime
import boto3

# Initialize AWS clients
s3_client = boto3.client('s3')

# Environment variables
RAW_BUCKET = os.environ.get('RAW_BUCKET')
PROCESSED_BUCKET = os.environ.get('PROCESSED_BUCKET')
ANALYTICS_BUCKET = os.environ.get('ANALYTICS_BUCKET')
LOW_CONF_THRESHOLD = float(os.environ.get('LOW_CONF_THRESHOLD', '0.85'))

def write_s3_text(bucket: str, key: str, text: str) -> None:
    """Write text content to S3 bucket."""
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=text.encode('utf-8'),
        ContentType='text/plain'
    )

def write_s3_json(bucket: str, key: str, data: dict) -> None:
    """Write JSON data to S3 bucket."""
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, indent=2),
        ContentType='application/json'
    )

def get_current_date() -> str:
    """Get current date in YYYY-MM-DD format."""
    return datetime.utcnow().strftime('%Y-%m-%d')
