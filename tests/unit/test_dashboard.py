"""
Unit tests for the dashboard components.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from dashboard.utils import (
    DashboardDataLoader,
    load_ml_model_metrics,
    get_data_quality_metrics,
    format_number,
    get_color_scheme
)

class TestDashboardDataLoader:
    """Test cases for DashboardDataLoader class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.data_loader = DashboardDataLoader()
    
    def test_initialization(self):
        """Test DashboardDataLoader initialization."""
        assert self.data_loader.aws_region == "us-east-1"
        assert hasattr(self.data_loader, 's3_client')
    
    def test_load_sample_data(self):
        """Test sample data loading."""
        data = self.data_loader.load_compliance_data(2024, "Financial")
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert "Risk Category" in data.columns
        assert "Region" in data.columns
        assert "Risk Value" in data.columns
        assert "Compliance Score" in data.columns
    
    def test_get_risk_level(self):
        """Test risk level classification."""
        assert self.data_loader._get_risk_level(25) == "Low"
        assert self.data_loader._get_risk_level(45) == "Medium"
        assert self.data_loader._get_risk_level(75) == "High"
    
    def test_fetch_compliance_score(self):
        """Test compliance score fetching."""
        score = self.data_loader.fetch_compliance_score(2024)
        assert isinstance(score, float)
        assert 0 <= score <= 100
    
    def test_get_risk_trends(self):
        """Test risk trends data."""
        trends = self.data_loader.get_risk_trends(2024)
        assert isinstance(trends, pd.DataFrame)
        assert "Date" in trends.columns
        assert "Risk Category" in trends.columns
        assert "Risk Value" in trends.columns
    
    def test_get_regional_analysis(self):
        """Test regional analysis data."""
        regional_data = self.data_loader.get_regional_analysis(2024)
        assert isinstance(regional_data, pd.DataFrame)
        assert len(regional_data) > 0

class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_load_ml_model_metrics(self):
        """Test ML model metrics loading."""
        metrics = load_ml_model_metrics()
        
        assert isinstance(metrics, dict)
        assert "baseline_model" in metrics
        assert "transformer_model" in metrics
        
        # Check baseline model metrics
        baseline = metrics["baseline_model"]
        assert "accuracy" in baseline
        assert "precision" in baseline
        assert "recall" in baseline
        assert "f1_score" in baseline
        
        # Check metric values are valid
        for metric in baseline.values():
            assert isinstance(metric, float)
            assert 0 <= metric <= 1
    
    def test_get_data_quality_metrics(self):
        """Test data quality metrics loading."""
        metrics = get_data_quality_metrics()
        
        assert isinstance(metrics, dict)
        expected_keys = ["completeness", "accuracy", "consistency", "timeliness", "validity"]
        
        for key in expected_keys:
            assert key in metrics
            assert isinstance(metrics[key], float)
            assert 0 <= metrics[key] <= 100
    
    def test_format_number(self):
        """Test number formatting."""
        assert format_number(1234.56) == "1.23K"
        assert format_number(1234567.89) == "1.23M"
        assert format_number(123.45) == "123.45"
        assert format_number(123.45, 1) == "123.5"
    
    def test_get_color_scheme(self):
        """Test color scheme retrieval."""
        colors = get_color_scheme()
        
        assert isinstance(colors, dict)
        expected_colors = ["primary", "secondary", "success", "warning", "info", "light", "dark"]
        
        for color in expected_colors:
            assert color in colors
            assert colors[color].startswith("#")

class TestDataValidation:
    """Test data validation and integrity."""
    
    def test_sample_data_integrity(self):
        """Test that sample data has proper structure and values."""
        data_loader = DashboardDataLoader()
        data = data_loader.load_compliance_data(2024, "all")
        
        # Check required columns
        required_columns = ["Date", "Risk Category", "Region", "Risk Value", "Risk Level", "Compliance Score"]
        for col in required_columns:
            assert col in data.columns
        
        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(pd.to_datetime(data["Date"]))
        assert pd.api.types.is_numeric_dtype(data["Risk Value"])
        assert pd.api.types.is_numeric_dtype(data["Compliance Score"])
        
        # Check value ranges
        assert data["Risk Value"].min() >= 0
        assert data["Risk Value"].max() <= 100
        assert data["Compliance Score"].min() >= 0
        assert data["Compliance Score"].max() <= 100
        
        # Check risk levels
        valid_risk_levels = ["Low", "Medium", "High"]
        assert all(level in valid_risk_levels for level in data["Risk Level"].unique())
    
    def test_regional_data_consistency(self):
        """Test regional data consistency."""
        data_loader = DashboardDataLoader()
        data = data_loader.load_compliance_data(2024, "all")
        
        # Check that all regions have data
        regions = data["Region"].unique()
        assert len(regions) > 0
        
        # Check that each region has reasonable data distribution
        for region in regions:
            region_data = data[data["Region"] == region]
            assert len(region_data) > 0
            
            # Check that risk values are reasonable
            assert region_data["Risk Value"].mean() > 0
            assert region_data["Risk Value"].mean() < 100

class TestErrorHandling:
    """Test error handling scenarios."""
    
    @patch('dashboard.utils.boto3.client')
    def test_aws_connection_failure(self, mock_boto3):
        """Test handling of AWS connection failures."""
        mock_boto3.side_effect = Exception("AWS connection failed")
        
        data_loader = DashboardDataLoader()
        
        # Should still work with sample data
        data = data_loader.load_compliance_data(2024, "Financial")
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
    
    def test_invalid_year_handling(self):
        """Test handling of invalid year parameters."""
        data_loader = DashboardDataLoader()
        
        # Should handle invalid years gracefully
        data = data_loader.load_compliance_data(9999, "Financial")
        assert isinstance(data, pd.DataFrame)
    
    def test_invalid_risk_type_handling(self):
        """Test handling of invalid risk type parameters."""
        data_loader = DashboardDataLoader()
        
        # Should handle invalid risk types gracefully
        data = data_loader.load_compliance_data(2024, "InvalidType")
        assert isinstance(data, pd.DataFrame)

if __name__ == "__main__":
    pytest.main([__file__])


