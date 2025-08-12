import os
import mlflow
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def init_mlflow(run_name: str, use_s3: bool = False, s3_bucket: str = None):
    """Initialize MLflow tracking with optional S3 artifact storage."""
    if use_s3 and s3_bucket:
        os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'https://s3.amazonaws.com'
        os.environ['AWS_DEFAULT_REGION'] = os.getenv('AWS_REGION', 'eu-west-2')
        mlflow.set_tracking_uri("file:./mlruns")
        mlflow.set_experiment("legal_risk_text")
        mlflow.start_run(run_name=run_name)
        mlflow.log_param('artifact_store', f's3://{s3_bucket}/mlflow')
    else:
        mlflow.set_tracking_uri("file:./mlruns")
        mlflow.set_experiment("legal_risk_text")
        mlflow.start_run(run_name=run_name)
    return mlflow
