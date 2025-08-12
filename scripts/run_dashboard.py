#!/usr/bin/env python3
"""
Dashboard Runner Script

This script provides a convenient way to run the Streamlit dashboard
with proper configuration and environment setup.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def setup_environment():
    """Setup environment variables and paths."""
    # Add src to Python path
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Set environment variables
    os.environ.setdefault("STREAMLIT_SERVER_PORT", "8501")
    os.environ.setdefault("STREAMLIT_SERVER_ADDRESS", "localhost")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    
    # AWS configuration
    os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
    
    print("✅ Environment setup completed")

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        "streamlit",
        "pandas", 
        "plotly",
        "boto3",
        "numpy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def run_dashboard(port=8501, host="localhost", config_file=None):
    """Run the Streamlit dashboard."""
    
    # Get the dashboard file path
    dashboard_path = Path(__file__).parent.parent / "src" / "dashboard" / "main.py"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        return False
    
    # Build streamlit command
    cmd = [
        "streamlit", "run",
        str(dashboard_path),
        "--server.port", str(port),
        "--server.address", host,
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    if config_file:
        cmd.extend(["--config", config_file])
    
    print(f"🚀 Starting dashboard on http://{host}:{port}")
    print(f"📁 Dashboard file: {dashboard_path}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start dashboard: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
        return True
    
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run the Data Quality Compliance Dashboard")
    parser.add_argument(
        "--port", 
        type=int, 
        default=8501,
        help="Port to run the dashboard on (default: 8501)"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="localhost",
        help="Host to bind the dashboard to (default: localhost)"
    )
    parser.add_argument(
        "--config", 
        type=str,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--check-deps", 
        action="store_true",
        help="Check dependencies and exit"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📊 Data Quality Compliance Dashboard")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    if args.check_deps:
        print("✅ Dependency check completed successfully")
        return
    
    # Run dashboard
    success = run_dashboard(
        port=args.port,
        host=args.host,
        config_file=args.config
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()


