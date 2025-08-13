@echo off
echo 🚀 Data Quality Compliance Platform - Windows Setup
echo ================================================
echo.
echo This will set up everything automatically:
echo ✅ Create virtual environment
echo ✅ Install all dependencies  
echo ✅ Generate sample data
echo ✅ Train ML models
echo ✅ Launch dashboard
echo.
echo Starting setup...
echo.

python setup.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Setup completed successfully!
    echo 🎉 Your dashboard should now be running at: http://localhost:8501
    echo.
    pause
) else (
    echo.
    echo ❌ Setup failed. Please check the error messages above.
    echo.
    pause
)
