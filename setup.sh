#!/bin/bash

echo "🚀 Data Quality Compliance Platform - Setup"
echo "================================================"
echo ""
echo "This will set up everything automatically:"
echo "✅ Create virtual environment"
echo "✅ Install all dependencies"
echo "✅ Generate sample data"
echo "✅ Train ML models"
echo "✅ Launch dashboard"
echo ""
echo "Starting setup..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Run the setup
python3 setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup completed successfully!"
    echo "🎉 Your dashboard should now be running at: http://localhost:8501"
    echo ""
else
    echo ""
    echo "❌ Setup failed. Please check the error messages above."
    echo ""
    exit 1
fi
