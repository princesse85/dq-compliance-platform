import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from src.data_quality.quality_assessment import DataQualityAssessment
from src.data_quality.data_validation_suite import DataValidationSuite
from src.data_quality.generate_synthetic_data import SyntheticDataGenerator
from src.data_quality.utils import DataQualityUtils


class TestDataQualityAssessment:
    """Unit tests for DataQualityAssessment"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'age': [25, 30, 35, 28, 32],
            'salary': [50000, 60000, 75000, 55000, 70000],
            'department': ['IT', 'HR', 'IT', 'Finance', 'IT'],
            'email': ['alice@company.com', 'bob@company.com', 'charlie@company.com', 
                     'diana@company.com', 'eve@company.com']
        })
        self.assessment = DataQualityAssessment()
    
    def test_completeness_check(self):
        """Test completeness assessment"""
        # Add some missing values
        test_data_with_nulls = self.test_data.copy()
        test_data_with_nulls.loc[1, 'age'] = np.nan
        test_data_with_nulls.loc[2, 'email'] = None
        
        result = self.assessment.check_completeness(test_data_with_nulls)
        
        assert 'completeness_score' in result
        assert result['completeness_score'] < 1.0
        assert 'missing_values' in result
        assert len(result['missing_values']) > 0
    
    def test_accuracy_check(self):
        """Test accuracy assessment"""
        # Add some invalid data
        test_data_with_errors = self.test_data.copy()
        test_data_with_errors.loc[0, 'age'] = -5  # Invalid age
        test_data_with_errors.loc[1, 'email'] = 'invalid-email'  # Invalid email
        
        result = self.assessment.check_accuracy(test_data_with_errors)
        
        assert 'accuracy_score' in result
        assert result['accuracy_score'] < 1.0
        assert 'validation_errors' in result
    
    def test_consistency_check(self):
        """Test consistency assessment"""
        # Add inconsistent data
        test_data_inconsistent = self.test_data.copy()
        test_data_inconsistent.loc[0, 'department'] = 'IT'
        test_data_inconsistent.loc[0, 'salary'] = 30000  # Low salary for IT
        
        result = self.assessment.check_consistency(test_data_inconsistent)
        
        assert 'consistency_score' in result
        assert 'consistency_issues' in result
    
    def test_timeliness_check(self):
        """Test timeliness assessment"""
        # Add timestamp column
        test_data_with_timestamps = self.test_data.copy()
        test_data_with_timestamps['created_at'] = pd.date_range(
            start='2024-01-01', periods=len(test_data_with_timestamps), freq='D'
        )
        
        result = self.assessment.check_timeliness(test_data_with_timestamps, 'created_at')
        
        assert 'timeliness_score' in result
        assert 'freshness_issues' in result
    
    def test_comprehensive_assessment(self):
        """Test comprehensive quality assessment"""
        result = self.assessment.assess_quality(self.test_data)
        
        assert 'overall_score' in result
        assert 'completeness_score' in result
        assert 'accuracy_score' in result
        assert 'consistency_score' in result
        assert 'recommendations' in result
        assert isinstance(result['overall_score'], float)
        assert 0 <= result['overall_score'] <= 1


class TestDataValidationSuite:
    """Unit tests for DataValidationSuite"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'age': [25, 30, 35, 28, 32],
            'email': ['alice@company.com', 'bob@company.com', 'charlie@company.com', 
                     'diana@company.com', 'eve@company.com']
        })
        self.validation_suite = DataValidationSuite()
    
    def test_schema_validation(self):
        """Test schema validation"""
        schema = {
            'id': 'int64',
            'name': 'object',
            'age': 'int64',
            'email': 'object'
        }
        
        result = self.validation_suite.validate_schema(self.test_data, schema)
        
        assert result['is_valid'] == True
        assert 'schema_errors' in result
    
    def test_schema_validation_with_errors(self):
        """Test schema validation with type mismatches"""
        schema = {
            'id': 'float64',  # Wrong type
            'name': 'object',
            'age': 'int64',
            'email': 'object'
        }
        
        result = self.validation_suite.validate_schema(self.test_data, schema)
        
        assert result['is_valid'] == False
        assert len(result['schema_errors']) > 0
    
    def test_range_validation(self):
        """Test range validation"""
        constraints = {
            'age': {'min': 18, 'max': 65},
            'id': {'min': 1, 'max': 100}
        }
        
        result = self.validation_suite.validate_ranges(self.test_data, constraints)
        
        assert result['is_valid'] == True
        assert 'range_violations' in result
    
    def test_format_validation(self):
        """Test format validation"""
        formats = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'name': r'^[A-Za-z\s]+$'
        }
        
        result = self.validation_suite.validate_formats(self.test_data, formats)
        
        assert result['is_valid'] == True
        assert 'format_violations' in result
    
    def test_uniqueness_validation(self):
        """Test uniqueness validation"""
        unique_columns = ['id', 'email']
        
        result = self.validation_suite.validate_uniqueness(self.test_data, unique_columns)
        
        assert result['is_valid'] == True
        assert 'duplicate_records' in result


class TestSyntheticDataGenerator:
    """Unit tests for SyntheticDataGenerator"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'age': [25, 30, 35, 28, 32],
            'salary': [50000, 60000, 75000, 55000, 70000],
            'department': ['IT', 'HR', 'IT', 'Finance', 'IT']
        })
        self.generator = SyntheticDataGenerator()
    
    def test_generate_synthetic_data(self):
        """Test synthetic data generation"""
        synthetic_data = self.generator.generate_synthetic_data(
            self.test_data, 
            num_records=10,
            preserve_distributions=True
        )
        
        assert len(synthetic_data) == 10
        assert list(synthetic_data.columns) == list(self.test_data.columns)
        assert synthetic_data['id'].dtype == self.test_data['id'].dtype
    
    def test_preserve_data_types(self):
        """Test that synthetic data preserves original data types"""
        synthetic_data = self.generator.generate_synthetic_data(
            self.test_data, 
            num_records=5
        )
        
        for col in self.test_data.columns:
            assert synthetic_data[col].dtype == self.test_data[col].dtype
    
    def test_maintain_categorical_distributions(self):
        """Test that categorical distributions are maintained"""
        synthetic_data = self.generator.generate_synthetic_data(
            self.test_data, 
            num_records=100
        )
        
        # Check that department distribution is similar
        original_dept_counts = self.test_data['department'].value_counts(normalize=True)
        synthetic_dept_counts = synthetic_data['department'].value_counts(normalize=True)
        
        # Should have similar proportions (allowing for some variance)
        for dept in original_dept_counts.index:
            assert abs(original_dept_counts[dept] - synthetic_dept_counts.get(dept, 0)) < 0.3
    
    def test_numerical_range_preservation(self):
        """Test that numerical ranges are preserved"""
        synthetic_data = self.generator.generate_synthetic_data(
            self.test_data, 
            num_records=50
        )
        
        # Age should be within reasonable bounds
        assert synthetic_data['age'].min() >= 18
        assert synthetic_data['age'].max() <= 70
        
        # Salary should be within reasonable bounds
        assert synthetic_data['salary'].min() >= 30000
        assert synthetic_data['salary'].max() <= 200000


class TestDataQualityUtils:
    """Unit tests for DataQualityUtils"""
    
    def setup_method(self):
        """Setup test data"""
        self.utils = DataQualityUtils()
        self.test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'age': [25, 30, 35, 28, 32],
            'salary': [50000, 60000, 75000, 55000, 70000]
        })
    
    def test_calculate_statistics(self):
        """Test statistical calculations"""
        stats = self.utils.calculate_statistics(self.test_data)
        
        assert 'numeric_columns' in stats
        assert 'categorical_columns' in stats
        assert 'missing_values' in stats
        assert 'duplicates' in stats
    
    def test_detect_outliers(self):
        """Test outlier detection"""
        outliers = self.utils.detect_outliers(self.test_data, 'salary')
        
        assert isinstance(outliers, list)
        assert len(outliers) >= 0
    
    def test_validate_email_format(self):
        """Test email validation"""
        valid_emails = ['test@example.com', 'user.name@domain.co.uk']
        invalid_emails = ['invalid-email', 'test@', '@domain.com']
        
        for email in valid_emails:
            assert self.utils.validate_email_format(email) == True
        
        for email in invalid_emails:
            assert self.utils.validate_email_format(email) == False
    
    def test_clean_data(self):
        """Test data cleaning functionality"""
        dirty_data = self.test_data.copy()
        dirty_data.loc[0, 'name'] = '  Alice  '  # Extra whitespace
        dirty_data.loc[1, 'age'] = '30'  # String instead of int
        
        cleaned_data = self.utils.clean_data(dirty_data)
        
        assert cleaned_data.loc[0, 'name'] == 'Alice'  # Whitespace removed
        assert cleaned_data.loc[1, 'age'] == 30  # Converted to int
    
    def test_generate_quality_report(self):
        """Test quality report generation"""
        report = self.utils.generate_quality_report(self.test_data)
        
        assert 'summary' in report
        assert 'detailed_analysis' in report
        assert 'recommendations' in report
        assert isinstance(report['summary'], dict)


