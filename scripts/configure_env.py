#!/usr/bin/env python3
"""
Environment Configuration Script

This script helps users configure their environment for the Data Quality Compliance Platform.
It validates AWS credentials, creates necessary directories, and sets up environment variables.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional

def print_status(message: str, status: str = "INFO"):
    """Print formatted status message."""
    colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
    }
    color = colors.get(status, colors["INFO"])
    reset = "\033[0m"
    print(f"{color}[{status}]{reset} {message}")

def check_aws_credentials() -> bool:
    """Check if AWS credentials are configured."""
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            capture_output=True,
            text=True,
            check=True
        )
        identity = json.loads(result.stdout)
        print_status(f"AWS credentials valid - Account: {identity['Account']}", "SUCCESS")
        return True
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        print_status("AWS credentials not configured or invalid", "WARNING")
        return False

def get_aws_account_id() -> Optional[str]:
    """Get AWS account ID."""
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity", "--query", "Account", "--output", "text"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def get_aws_region() -> str:
    """Get AWS region from configuration."""
    try:
        result = subprocess.run(
            ["aws", "configure", "get", "region"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "us-east-1"

def create_directories():
    """Create necessary directories."""
    directories = [
        "analytics/models/baseline",
        "analytics/models/transformer/checkpoints",
        "analytics/models/transformer/final_model",
        "src/data/text_corpus",
        "src/data/raw",
        "logs",
        ".streamlit",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_status(f"Created directory: {directory}", "SUCCESS")

def create_env_file(aws_account_id: Optional[str] = None, aws_region: str = "us-east-1"):
    """Create .env file with configuration."""
    env_template = f"""# =============================================================================
# ENVIRONMENT CONFIGURATION - AUTO-GENERATED
# =============================================================================

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_DEFAULT_REGION={aws_region}
AWS_REGION={aws_region}

# AWS S3 Buckets
COMPLIANCE_BUCKET=enterprise-compliance-data-{aws_account_id or 'your-account-id'}
RAW_DATA_BUCKET=enterprise-raw-data-{aws_account_id or 'your-account-id'}
PROCESSED_DATA_BUCKET=enterprise-processed-data-{aws_account_id or 'your-account-id'}
ML_MODELS_BUCKET=enterprise-ml-models-{aws_account_id or 'your-account-id'}

# Dashboard Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_SERVER_HEADLESS=true
DASHBOARD_REFRESH_INTERVAL=30
DASHBOARD_MAX_UPLOAD_SIZE=200

# ML Model Configuration
MODEL_NAME=distilbert-base-uncased
EPOCHS=1
BATCH_SIZE=16
LEARNING_RATE=2e-5
MAX_LENGTH=128

# ETL Configuration
SPARK_MASTER=local[*]
SPARK_DRIVER_MEMORY=2g
SPARK_EXECUTOR_MEMORY=2g
ETL_RAW_PREFIX=contract_register/
ETL_PROCESSED_PREFIX=contract_register/

# Development Configuration
DEBUG=false
ENVIRONMENT=development
USE_LOCAL_DATA=true
MOCK_AWS_SERVICES=false

# Feature Flags
ENABLE_DOCUMENT_ANALYSIS=true
ENABLE_ML_PREDICTIONS=true
ENABLE_REAL_TIME_ALERTS=false
ENABLE_DATA_EXPORT=true
"""
    
    with open(".env", "w") as f:
        f.write(env_template)
    
    print_status("Created .env file", "SUCCESS")

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        "streamlit", "pandas", "numpy", "plotly", "boto3",
        "scikit-learn", "transformers", "torch", "datasets"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print_status(f"✅ {package}", "SUCCESS")
        except ImportError:
            missing_packages.append(package)
            print_status(f"❌ {package}", "ERROR")
    
    if missing_packages:
        print_status(f"Missing packages: {', '.join(missing_packages)}", "WARNING")
        print_status("Run: pip install -r requirements.txt", "INFO")
        return False
    
    return True

def create_streamlit_config():
    """Create Streamlit configuration."""
    config_content = """[server]
port = 8501
address = "localhost"
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
"""
    
    config_path = Path(".streamlit/config.toml")
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, "w") as f:
        f.write(config_content)
    
    print_status("Created Streamlit configuration", "SUCCESS")

def validate_setup():
    """Validate the complete setup."""
    print_status("Validating setup...", "INFO")
    
    # Check if .env exists
    if not Path(".env").exists():
        print_status("❌ .env file not found", "ERROR")
        return False
    
    # Check if directories exist
    required_dirs = [
        "analytics/models/baseline",
        "analytics/models/transformer",
        "src/data/text_corpus",
        ".streamlit"
    ]
    
    for directory in required_dirs:
        if not Path(directory).exists():
            print_status(f"❌ Directory not found: {directory}", "ERROR")
            return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    print_status("✅ Setup validation completed", "SUCCESS")
    return True

def main():
    """Main configuration function."""
    print_status("🚀 Data Quality Compliance Platform - Environment Configuration", "INFO")
    print_status("=" * 60, "INFO")
    
    # Check AWS credentials
    aws_configured = check_aws_credentials()
    aws_account_id = get_aws_account_id() if aws_configured else None
    aws_region = get_aws_region()
    
    # Create directories
    print_status("Creating directories...", "INFO")
    create_directories()
    
    # Create environment file
    print_status("Creating environment configuration...", "INFO")
    create_env_file(aws_account_id, aws_region)
    
    # Create Streamlit config
    print_status("Creating Streamlit configuration...", "INFO")
    create_streamlit_config()
    
    # Validate setup
    if validate_setup():
        print_status("=" * 60, "INFO")
        print_status("✅ Environment configuration completed successfully!", "SUCCESS")
        
        if aws_configured:
            print_status("Next steps:", "INFO")
            print_status("1. Update .env with your AWS credentials", "INFO")
            print_status("2. Run: cdk bootstrap", "INFO")
            print_status("3. Run: cdk deploy --all", "INFO")
            print_status("4. Run: python scripts/generate_data_and_train.py", "INFO")
            print_status("5. Run: streamlit run streamlit_app.py", "INFO")
        else:
            print_status("Next steps (Local Development):", "INFO")
            print_status("1. Run: pip install -r requirements.txt", "INFO")
            print_status("2. Run: python scripts/generate_data_and_train.py", "INFO")
            print_status("3. Run: streamlit run streamlit_app.py", "INFO")
    else:
        print_status("❌ Setup validation failed", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
