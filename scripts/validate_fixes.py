#!/usr/bin/env python3
"""
Validation script for Enterprise Data Quality & Compliance Platform fixes.

This script validates that all critical issues have been resolved and the
platform is ready for deployment.
"""

import os
import sys
import importlib
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidationResult:
    """Container for validation results."""
    
    def __init__(self, name: str, status: bool, message: str = ""):
        self.name = name
        self.status = status
        self.message = message

def validate_logging_config() -> ValidationResult:
    """Validate that logging configuration is working."""
    try:
        from src.utils.logging_config import get_logger, setup_logging
        
        # Test logger creation
        test_logger = get_logger("test")
        if not test_logger:
            return ValidationResult("Logging Config", False, "Failed to create logger")
        
        # Test setup_logging
        setup_logger = setup_logging("test_setup")
        if not setup_logger:
            return ValidationResult("Logging Config", False, "Failed to setup logging")
        
        return ValidationResult("Logging Config", True, "Logging configuration working")
        
    except Exception as e:
        return ValidationResult("Logging Config", False, f"Error: {str(e)}")

def validate_etl_job() -> ValidationResult:
    """Validate ETL job script."""
    try:
        etl_path = Path("src/etl_pipelines/contracts_etl_job.py")
        if not etl_path.exists():
            return ValidationResult("ETL Job", False, "ETL job file not found")
        
        # Check for hardcoded region
        with open(etl_path, 'r') as f:
            content = f.read()
            if "eu-west-2" in content and "os.environ" not in content:
                return ValidationResult("ETL Job", False, "Hardcoded region found")
        
        # Check for proper error handling
        if "try:" not in content or "except Exception" not in content:
            return ValidationResult("ETL Job", False, "Missing error handling")
        
        return ValidationResult("ETL Job", True, "ETL job validation passed")
        
    except Exception as e:
        return ValidationResult("ETL Job", False, f"Error: {str(e)}")

def validate_lambda_functions() -> ValidationResult:
    """Validate Lambda function implementations."""
    try:
        lambda_files = [
            "src/ocr/lambda_ingest_router.py",
            "src/ocr/lambda_textract_consumer.py",
            "lambda_app/app/handler.py"
        ]
        
        for file_path in lambda_files:
            if not Path(file_path).exists():
                return ValidationResult("Lambda Functions", False, f"Missing file: {file_path}")
            
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Check for broken imports
                if "from src.utils.logging_config import get_logger" in content:
                    return ValidationResult("Lambda Functions", False, f"Broken import in {file_path}")
                
                # Check for error handling
                if "try:" not in content or "except Exception" not in content:
                    return ValidationResult("Lambda Functions", False, f"Missing error handling in {file_path}")
        
        return ValidationResult("Lambda Functions", True, "All Lambda functions validated")
        
    except Exception as e:
        return ValidationResult("Lambda Functions", False, f"Error: {str(e)}")

def validate_infrastructure_stacks() -> ValidationResult:
    """Validate CDK infrastructure stacks."""
    try:
        stack_files = [
            "infrastructure/foundation_stack.py",
            "infrastructure/data_quality_stack.py",
            "infrastructure/document_processing_stack.py",
            "infrastructure/ml_inference_stack.py"
        ]
        
        for file_path in stack_files:
            if not Path(file_path).exists():
                return ValidationResult("Infrastructure Stacks", False, f"Missing stack: {file_path}")
            
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Check for proper imports
                if "from aws_cdk import" not in content:
                    return ValidationResult("Infrastructure Stacks", False, f"Missing CDK imports in {file_path}")
        
        return ValidationResult("Infrastructure Stacks", True, "All infrastructure stacks validated")
        
    except Exception as e:
        return ValidationResult("Infrastructure Stacks", False, f"Error: {str(e)}")

def validate_dependencies() -> ValidationResult:
    """Validate Python dependencies."""
    try:
        required_files = [
            "requirements.txt",
            "lambda_app/requirements.txt"
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                return ValidationResult("Dependencies", False, f"Missing requirements file: {file_path}")
        
        # Check for critical dependencies
        with open("requirements.txt", 'r') as f:
            content = f.read()
            critical_deps = ["aws-cdk-lib", "boto3", "pandas", "pyspark"]
            
            for dep in critical_deps:
                if dep not in content:
                    return ValidationResult("Dependencies", False, f"Missing critical dependency: {dep}")
        
        return ValidationResult("Dependencies", True, "All dependencies validated")
        
    except Exception as e:
        return ValidationResult("Dependencies", False, f"Error: {str(e)}")

def validate_configuration() -> ValidationResult:
    """Validate configuration files."""
    try:
        config_files = [
            "config/environment.example",
            "cdk.json",
            "docker-compose.yml"
        ]
        
        for file_path in config_files:
            if not Path(file_path).exists():
                return ValidationResult("Configuration", False, f"Missing config file: {file_path}")
        
        return ValidationResult("Configuration", True, "All configuration files present")
        
    except Exception as e:
        return ValidationResult("Configuration", False, f"Error: {str(e)}")

def validate_project_structure() -> ValidationResult:
    """Validate project directory structure."""
    try:
        required_dirs = [
            "src",
            "src/data_quality",
            "src/etl_pipelines",
            "src/ocr",
            "src/ml",
            "src/utils",
            "infrastructure",
            "lambda_app",
            "tests"
        ]
        
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                return ValidationResult("Project Structure", False, f"Missing directory: {dir_path}")
        
        return ValidationResult("Project Structure", True, "Project structure validated")
        
    except Exception as e:
        return ValidationResult("Project Structure", False, f"Error: {str(e)}")

def run_validation() -> List[ValidationResult]:
    """Run all validation checks."""
    validators = [
        validate_logging_config,
        validate_etl_job,
        validate_lambda_functions,
        validate_infrastructure_stacks,
        validate_dependencies,
        validate_configuration,
        validate_project_structure
    ]
    
    results = []
    for validator in validators:
        try:
            result = validator()
            results.append(result)
        except Exception as e:
            results.append(ValidationResult(validator.__name__, False, f"Validation failed: {str(e)}"))
    
    return results

def print_results(results: List[ValidationResult]) -> None:
    """Print validation results."""
    logger.info("=" * 60)
    logger.info("VALIDATION RESULTS")
    logger.info("=" * 60)
    
    passed = 0
    failed = 0
    
    for result in results:
        status = "✅ PASS" if result.status else "❌ FAIL"
        logger.info(f"{status} - {result.name}")
        if result.message:
            logger.info(f"    {result.message}")
        
        if result.status:
            passed += 1
        else:
            failed += 1
    
    logger.info("=" * 60)
    logger.info(f"SUMMARY: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All validations passed! The platform is ready for deployment.")
        return True
    else:
        logger.error("⚠️  Some validations failed. Please fix the issues before deployment.")
        return False

def main():
    """Main validation function."""
    logger.info("Starting platform validation...")
    
    # Run all validations
    results = run_validation()
    
    # Print results
    success = print_results(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
