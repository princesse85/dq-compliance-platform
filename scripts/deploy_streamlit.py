#!/usr/bin/env python3
"""
Streamlit Cloud Deployment Script

This script helps prepare the dashboard for deployment on Streamlit Cloud.
It sets up environment variables and validates the configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all required files exist."""
    required_files = [
        "streamlit_app.py",
        "requirements.txt",
        "src/dashboard/main.py",
        "src/dashboard/utils.py",
        "src/dashboard/__init__.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def validate_imports():
    """Validate that all imports work correctly."""
    try:
        # Test the main dashboard import
        sys.path.insert(0, str(Path("src")))
        from dashboard.main import main
        from dashboard.utils import DashboardDataLoader
        print("✅ All imports validated successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def create_streamlit_config():
    """Create Streamlit configuration file."""
    config_content = """[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#3b82f6"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#1e293b"
"""
    
    config_dir = Path(".streamlit")
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.toml"
    with open(config_file, "w") as f:
        f.write(config_content)
    
    print("✅ Streamlit configuration created")

def create_secrets_template():
    """Create a template for Streamlit secrets."""
    secrets_content = """# Streamlit Cloud Secrets Configuration
# Copy this to your Streamlit Cloud secrets management

# AWS Configuration (optional - for production)
AWS_ACCESS_KEY_ID = "your_aws_access_key_id"
AWS_SECRET_ACCESS_KEY = "your_aws_secret_access_key"
AWS_DEFAULT_REGION = "us-east-1"

# Dashboard Configuration
COMPLIANCE_BUCKET = "your-s3-bucket-name"

# ML Model Configuration (optional)
ML_MODEL_ENDPOINT = "your-ml-endpoint-url"
API_KEY = "your-api-key"
"""
    
    with open("streamlit_secrets_template.toml", "w") as f:
        f.write(secrets_content)
    
    print("✅ Streamlit secrets template created")

def check_git_status():
    """Check git status and provide deployment instructions."""
    try:
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("⚠️  Uncommitted changes detected:")
            print(result.stdout)
            print("\n💡 Consider committing changes before deployment:")
            print("   git add .")
            print("   git commit -m 'Prepare for Streamlit Cloud deployment'")
        else:
            print("✅ All changes committed")
            
    except subprocess.CalledProcessError:
        print("⚠️  Git not available or not a git repository")

def main():
    """Main deployment preparation function."""
    print("🚀 Streamlit Cloud Deployment Preparation")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Validate imports
    if not validate_imports():
        sys.exit(1)
    
    # Create configuration files
    create_streamlit_config()
    create_secrets_template()
    
    # Check git status
    check_git_status()
    
    print("\n" + "=" * 50)
    print("✅ Deployment preparation complete!")
    print("\n📋 Next steps:")
    print("1. Push your code to GitHub:")
    print("   git push origin main")
    print("\n2. Deploy on Streamlit Cloud:")
    print("   - Go to https://share.streamlit.io")
    print("   - Connect your GitHub repository")
    print("   - Set main file path to: streamlit_app.py")
    print("   - Add any required secrets in the Streamlit Cloud dashboard")
    print("\n3. Your dashboard will be available at:")
    print("   https://your-app-name.streamlit.app")
    
    print("\n🔧 Configuration files created:")
    print("   - .streamlit/config.toml (Streamlit configuration)")
    print("   - streamlit_secrets_template.toml (Secrets template)")

if __name__ == "__main__":
    main()
