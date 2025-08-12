"""
Enterprise Compliance Dashboard - Streamlit Cloud Entry Point

This is the main entry point for deploying the dashboard on Streamlit Cloud.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main dashboard
from dashboard.main import main

if __name__ == "__main__":
    main()
