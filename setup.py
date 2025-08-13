#!/usr/bin/env python3
"""
One-Command Setup for Data Quality Compliance Platform

This script provides a simple way to set up the entire platform with a single command.
Just run: python setup.py
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main setup function."""
    print("🚀 Data Quality Compliance Platform - One-Command Setup")
    print("=" * 60)
    print("This will set up everything automatically:")
    print("✅ Create virtual environment")
    print("✅ Install all dependencies")
    print("✅ Generate sample data")
    print("✅ Train ML models")
    print("✅ Launch dashboard")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("scripts/setup_complete.py").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   cd /path/to/dq-compliance-platform")
        print("   python setup.py")
        sys.exit(1)
    
    # Run the complete setup script
    try:
        result = subprocess.run([sys.executable, "scripts/setup_complete.py"], 
                              check=True, capture_output=False)
        print("\n✅ Setup completed successfully!")
        print("🎉 Your dashboard should now be running at: http://localhost:8501")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Setup failed with error code: {e.returncode}")
        print("Please check the error messages above and try again.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        sys.exit(1)

if __name__ == "__main__":
    main()
