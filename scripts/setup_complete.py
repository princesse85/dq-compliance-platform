#!/usr/bin/env python3
"""
Complete Setup Script for Data Quality Compliance Platform

This script provides a one-stop setup for the entire platform, including:
- Environment configuration
- Dependency installation
- AWS setup (optional)
- Data generation
- Model training
- Dashboard launch
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional, List

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

def run_command(command: List[str], capture_output: bool = True) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(command, capture_output=capture_output, text=True, check=True)
        if not capture_output and result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        if capture_output and e.stderr:
            print_status(f"Command failed: {' '.join(command)}", "ERROR")
            print_status(f"Error: {e.stderr}", "ERROR")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_status("Python 3.8+ is required", "ERROR")
        return False
    print_status(f"Python {version.major}.{version.minor}.{version.micro} - OK", "SUCCESS")
    return True

def install_dependencies():
    """Install all required dependencies."""
    print_status("Installing dependencies...", "INFO")
    
    # Install main requirements
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
        print_status("Failed to install main requirements", "ERROR")
        return False
    
    # Install dev requirements if available
    if Path("requirements-dev.txt").exists():
        if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"]):
            print_status("Failed to install dev requirements (continuing...)", "WARNING")
    
    print_status("Dependencies installed successfully", "SUCCESS")
    return True

def setup_virtual_environment():
    """Setup virtual environment if not already active."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_status("Virtual environment already active", "SUCCESS")
        return True
    
    print_status("Creating virtual environment...", "INFO")
    if not run_command([sys.executable, "-m", "venv", ".venv"]):
        print_status("Failed to create virtual environment", "ERROR")
        return False
    
    print_status("Virtual environment created. Please activate it and run this script again.", "WARNING")
    print_status("On Windows: .venv\\Scripts\\activate", "INFO")
    print_status("On macOS/Linux: source .venv/bin/activate", "INFO")
    return False

def check_aws_setup():
    """Check AWS setup and return configuration."""
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            capture_output=True,
            text=True,
            check=True
        )
        identity = json.loads(result.stdout)
        
        # Get region
        region_result = subprocess.run(
            ["aws", "configure", "get", "region"],
            capture_output=True,
            text=True,
            check=True
        )
        region = region_result.stdout.strip()
        
        print_status(f"AWS configured - Account: {identity['Account']}, Region: {region}", "SUCCESS")
        return {
            "account_id": identity['Account'],
            "region": region,
            "configured": True
        }
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        print_status("AWS not configured - will use local development mode", "WARNING")
        return {"configured": False, "region": "us-east-1"}

def create_environment_file(aws_config: Dict):
    """Create comprehensive environment file."""
    env_content = f"""# =============================================================================
# COMPLETE ENVIRONMENT CONFIGURATION
# =============================================================================

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_DEFAULT_REGION={aws_config['region']}
AWS_REGION={aws_config['region']}

# AWS S3 Buckets (auto-generated)
COMPLIANCE_BUCKET=enterprise-compliance-data-{aws_config.get('account_id', 'your-account-id')}
RAW_DATA_BUCKET=enterprise-raw-data-{aws_config.get('account_id', 'your-account-id')}
PROCESSED_DATA_BUCKET=enterprise-processed-data-{aws_config.get('account_id', 'your-account-id')}
ML_MODELS_BUCKET=enterprise-ml-models-{aws_config.get('account_id', 'your-account-id')}

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
MOCK_AWS_SERVICES={str(not aws_config['configured']).lower()}

# Feature Flags
ENABLE_DOCUMENT_ANALYSIS=true
ENABLE_ML_PREDICTIONS=true
ENABLE_REAL_TIME_ALERTS=false
ENABLE_DATA_EXPORT=true

# Security (update these in production)
ENCRYPTION_KEY=your_encryption_key_here
ENABLE_DATA_ENCRYPTION=false

# Monitoring
LOG_LEVEL=INFO
ENABLE_CLOUDWATCH_LOGGING={str(aws_config['configured']).lower()}
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print_status("Environment file created", "SUCCESS")

def create_directories():
    """Create all necessary directories."""
    directories = [
        "analytics/models/baseline",
        "analytics/models/transformer/checkpoints",
        "analytics/models/transformer/final_model",
        "src/data/text_corpus",
        "src/data/raw",
        "src/data/processed",
        "logs",
        ".streamlit",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print_status("Directories created", "SUCCESS")

def generate_data_and_train_models():
    """Generate data and train ML models."""
    print_status("Generating data and training models...", "INFO")
    
    if not run_command([sys.executable, "scripts/generate_data_and_train.py"], capture_output=False):
        print_status("Data generation and model training failed", "ERROR")
        return False
    
    print_status("Data generation and model training completed", "SUCCESS")
    return True

def setup_streamlit_config():
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
    
    print_status("Streamlit configuration created", "SUCCESS")

def validate_setup():
    """Validate the complete setup."""
    print_status("Validating setup...", "INFO")
    
    # Check required files
    required_files = [".env", ".streamlit/config.toml"]
    for file_path in required_files:
        if not Path(file_path).exists():
            print_status(f"Missing required file: {file_path}", "ERROR")
            return False
    
    # Check required directories
    required_dirs = [
        "analytics/models/baseline",
        "analytics/models/transformer",
        "src/data/text_corpus"
    ]
    for directory in required_dirs:
        if not Path(directory).exists():
            print_status(f"Missing required directory: {directory}", "ERROR")
            return False
    
    # Check key dependencies
    key_packages = ["streamlit", "pandas", "numpy", "plotly"]
    for package in key_packages:
        try:
            __import__(package)
        except ImportError:
            print_status(f"Missing key package: {package}", "ERROR")
            return False
    
    print_status("Setup validation completed successfully", "SUCCESS")
    return True

def launch_dashboard():
    """Launch the Streamlit dashboard."""
    print_status("Launching dashboard...", "INFO")
    print_status("Dashboard will be available at: http://localhost:8501", "INFO")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
    except KeyboardInterrupt:
        print_status("Dashboard stopped by user", "INFO")

def main():
    """Main setup function."""
    print_status("🚀 Data Quality Compliance Platform - Complete Setup", "INFO")
    print_status("=" * 60, "INFO")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check AWS setup
    aws_config = check_aws_setup()
    
    # Create directories
    create_directories()
    
    # Create environment file
    create_environment_file(aws_config)
    
    # Setup Streamlit config
    setup_streamlit_config()
    
    # Generate data and train models
    if not generate_data_and_train_models():
        print_status("Continuing without ML models...", "WARNING")
    
    # Validate setup
    if not validate_setup():
        sys.exit(1)
    
    print_status("=" * 60, "INFO")
    print_status("✅ Complete setup finished successfully!", "SUCCESS")
    
    if aws_config['configured']:
        print_status("Next steps for AWS deployment:", "INFO")
        print_status("1. Update .env with your AWS credentials", "INFO")
        print_status("2. Run: cdk bootstrap", "INFO")
        print_status("3. Run: cdk deploy --all", "INFO")
    
    print_status("Next steps for local development:", "INFO")
    print_status("1. Run: streamlit run streamlit_app.py", "INFO")
    print_status("2. Open: http://localhost:8501", "INFO")
    
    # Ask if user wants to launch dashboard now
    try:
        response = input("\n🚀 Launch dashboard now? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            launch_dashboard()
    except KeyboardInterrupt:
        print_status("Setup completed. Run 'streamlit run streamlit_app.py' to start.", "INFO")

if __name__ == "__main__":
    main()
