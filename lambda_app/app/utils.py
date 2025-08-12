import os
import logging
import boto3
from typing import Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

def get_s3_presigned_url(s3_client, bucket: str, key: str, expiration: int = 3600) -> str:
    """Generate a pre-signed URL for S3 object access.
    
    Args:
        s3_client: Boto3 S3 client
        bucket: S3 bucket name
        key: S3 object key
        expiration: URL expiration time in seconds (default: 1 hour)
        
    Returns:
        Pre-signed URL string
    """
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        logger.error(f"Failed to generate pre-signed URL: {str(e)}")
        raise

def upload_file_to_s3(file_path: str, bucket: str, key: str, s3_client=None) -> bool:
    """Upload a file to S3.
    
    Args:
        file_path: Local file path
        bucket: S3 bucket name
        key: S3 object key
        s3_client: Optional S3 client (creates new one if not provided)
        
    Returns:
        True if upload successful, False otherwise
    """
    if s3_client is None:
        s3_client = boto3.client('s3')
    
    try:
        s3_client.upload_file(file_path, bucket, key)
        logger.info(f"Successfully uploaded {file_path} to s3://{bucket}/{key}")
        return True
    except ClientError as e:
        logger.error(f"Failed to upload file to S3: {str(e)}")
        return False

def download_file_from_s3(bucket: str, key: str, local_path: str, s3_client=None) -> bool:
    """Download a file from S3.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        local_path: Local file path to save to
        s3_client: Optional S3 client (creates new one if not provided)
        
    Returns:
        True if download successful, False otherwise
    """
    if s3_client is None:
        s3_client = boto3.client('s3')
    
    try:
        s3_client.download_file(bucket, key, local_path)
        logger.info(f"Successfully downloaded s3://{bucket}/{key} to {local_path}")
        return True
    except ClientError as e:
        logger.error(f"Failed to download file from S3: {str(e)}")
        return False

def check_s3_object_exists(bucket: str, key: str, s3_client=None) -> bool:
    """Check if an S3 object exists.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        s3_client: Optional S3 client (creates new one if not provided)
        
    Returns:
        True if object exists, False otherwise
    """
    if s3_client is None:
        s3_client = boto3.client('s3')
    
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            logger.error(f"Error checking S3 object existence: {str(e)}")
            return False

def list_s3_objects(bucket: str, prefix: str = "", s3_client=None, max_keys: int = 1000) -> list:
    """List objects in an S3 bucket with optional prefix.
    
    Args:
        bucket: S3 bucket name
        prefix: Optional prefix to filter by
        s3_client: Optional S3 client (creates new one if not provided)
        max_keys: Maximum number of keys to return
        
    Returns:
        List of S3 object keys
    """
    if s3_client is None:
        s3_client = boto3.client('s3')
    
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            MaxKeys=max_keys
        )
        
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        else:
            return []
            
    except ClientError as e:
        logger.error(f"Failed to list S3 objects: {str(e)}")
        return []

def get_environment_variable(key: str, default: str = None) -> Optional[str]:
    """Get environment variable with optional default.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        Environment variable value or default
    """
    value = os.getenv(key, default)
    if value is None:
        logger.warning(f"Environment variable {key} not set")
    return value

def validate_required_env_vars(required_vars: list) -> bool:
    """Validate that required environment variables are set.
    
    Args:
        required_vars: List of required environment variable names
        
    Returns:
        True if all required variables are set, False otherwise
    """
    missing_vars = []
    
    for var in required_vars:
        if not get_environment_variable(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    return True

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe S3 storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Replace problematic characters
    sanitized = filename.replace(' ', '_')
    sanitized = sanitized.replace('/', '_')
    sanitized = sanitized.replace('\\', '_')
    sanitized = sanitized.replace(':', '_')
    sanitized = sanitized.replace('*', '_')
    sanitized = sanitized.replace('?', '_')
    sanitized = sanitized.replace('"', '_')
    sanitized = sanitized.replace('<', '_')
    sanitized = sanitized.replace('>', '_')
    sanitized = sanitized.replace('|', '_')
    
    # Remove any remaining non-alphanumeric characters except dots and hyphens
    import re
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', sanitized)
    
    return sanitized

def get_file_extension(filename: str) -> str:
    """Get file extension from filename.
    
    Args:
        filename: Filename
        
    Returns:
        File extension (including the dot)
    """
    return os.path.splitext(filename)[1].lower()

def is_valid_file_extension(filename: str, allowed_extensions: list) -> bool:
    """Check if file has a valid extension.
    
    Args:
        filename: Filename to check
        allowed_extensions: List of allowed extensions (e.g., ['.txt', '.csv'])
        
    Returns:
        True if extension is allowed, False otherwise
    """
    ext = get_file_extension(filename)
    return ext in allowed_extensions
