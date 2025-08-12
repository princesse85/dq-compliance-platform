import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import json
from datetime import datetime, timedelta

from src.etl_pipelines.contracts_etl_job import ContractsETLJob


class TestContractsETLJob:
    """Unit tests for ContractsETLJob"""
    
    def setup_method(self):
        """Setup test data"""
        self.etl_job = ContractsETLJob()
        self.test_contracts_data = pd.DataFrame({
            'contract_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
            'client_name': ['Client A', 'Client B', 'Client C', 'Client D', 'Client E'],
            'contract_value': [100000, 250000, 75000, 500000, 150000],
            'start_date': ['2024-01-01', '2024-02-15', '2024-03-01', '2024-01-15', '2024-02-01'],
            'end_date': ['2024-12-31', '2024-12-31', '2024-08-31', '2025-01-31', '2024-11-30'],
            'status': ['Active', 'Active', 'Pending', 'Active', 'Completed'],
            'contract_type': ['Service', 'Product', 'Service', 'Product', 'Service'],
            'risk_level': ['Low', 'Medium', 'Low', 'High', 'Medium']
        })
    
    def test_data_validation(self):
        """Test data validation functionality"""
        # Test valid data
        validation_result = self.etl_job.validate_data(self.test_contracts_data)
        assert validation_result['is_valid'] == True
        assert len(validation_result['errors']) == 0
        
        # Test invalid data (missing required columns)
        invalid_data = self.test_contracts_data.drop(columns=['contract_id'])
        validation_result = self.etl_job.validate_data(invalid_data)
        assert validation_result['is_valid'] == False
        assert len(validation_result['errors']) > 0
    
    def test_data_cleaning(self):
        """Test data cleaning functionality"""
        # Create dirty data
        dirty_data = self.test_contracts_data.copy()
        dirty_data.loc[0, 'client_name'] = '  Client A  '  # Extra whitespace
        dirty_data.loc[1, 'contract_value'] = '250,000'  # String with comma
        dirty_data.loc[2, 'start_date'] = '2024-03-01 00:00:00'  # Extra time info
        
        cleaned_data = self.etl_job.clean_data(dirty_data)
        
        # Check cleaning results
        assert cleaned_data.loc[0, 'client_name'] == 'Client A'  # Whitespace removed
        assert cleaned_data.loc[1, 'contract_value'] == 250000  # Converted to int
        assert cleaned_data.loc[2, 'start_date'] == '2024-03-01'  # Date only
    
    def test_data_transformation(self):
        """Test data transformation functionality"""
        transformed_data = self.etl_job.transform_data(self.test_contracts_data)
        
        # Check that new columns are created
        assert 'contract_duration_days' in transformed_data.columns
        assert 'monthly_value' in transformed_data.columns
        assert 'is_high_value' in transformed_data.columns
        assert 'risk_score' in transformed_data.columns
        
        # Check data types
        assert transformed_data['contract_duration_days'].dtype in ['int64', 'int32']
        assert transformed_data['monthly_value'].dtype in ['float64', 'float32']
        assert transformed_data['is_high_value'].dtype == 'bool'
    
    def test_contract_duration_calculation(self):
        """Test contract duration calculation"""
        # Test with valid dates
        start_date = '2024-01-01'
        end_date = '2024-12-31'
        duration = self.etl_job.calculate_contract_duration(start_date, end_date)
        
        assert duration == 365  # 366 in leap year, but 365 for 2024
        
        # Test with invalid dates
        with pytest.raises(ValueError):
            self.etl_job.calculate_contract_duration('invalid-date', '2024-12-31')
    
    def test_risk_scoring(self):
        """Test risk scoring functionality"""
        risk_scores = self.etl_job.calculate_risk_scores(self.test_contracts_data)
        
        assert len(risk_scores) == len(self.test_contracts_data)
        assert all(0 <= score <= 100 for score in risk_scores)
        
        # High value contracts should have higher risk scores
        high_value_contracts = self.test_contracts_data[
            self.test_contracts_data['contract_value'] > 200000
        ]
        high_value_indices = high_value_contracts.index
        
        for idx in high_value_indices:
            assert risk_scores[idx] > 50  # Higher risk for high value contracts
    
    def test_data_enrichment(self):
        """Test data enrichment functionality"""
        enriched_data = self.etl_job.enrich_data(self.test_contracts_data)
        
        # Check for enriched columns
        assert 'client_segment' in enriched_data.columns
        assert 'contract_category' in enriched_data.columns
        assert 'renewal_probability' in enriched_data.columns
        
        # Check data types and ranges
        assert all(0 <= prob <= 1 for prob in enriched_data['renewal_probability'])
        assert enriched_data['client_segment'].isin(['Enterprise', 'Mid-Market', 'SMB']).all()
    
    def test_quality_checks(self):
        """Test data quality checks"""
        quality_report = self.etl_job.perform_quality_checks(self.test_contracts_data)
        
        assert 'completeness_score' in quality_report
        assert 'accuracy_score' in quality_report
        assert 'consistency_score' in quality_report
        assert 'overall_score' in quality_report
        assert all(0 <= score <= 1 for score in quality_report.values())
    
    def test_data_aggregation(self):
        """Test data aggregation functionality"""
        aggregated_data = self.etl_job.aggregate_data(self.test_contracts_data)
        
        # Check aggregation by different dimensions
        assert 'total_contracts' in aggregated_data.columns
        assert 'total_value' in aggregated_data.columns
        assert 'avg_contract_value' in aggregated_data.columns
        
        # Verify calculations
        expected_total_value = self.test_contracts_data['contract_value'].sum()
        assert aggregated_data['total_value'].iloc[0] == expected_total_value
    
    def test_data_export(self):
        """Test data export functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test CSV export
            csv_path = os.path.join(temp_dir, 'contracts.csv')
            self.etl_job.export_to_csv(self.test_contracts_data, csv_path)
            
            assert os.path.exists(csv_path)
            
            # Test JSON export
            json_path = os.path.join(temp_dir, 'contracts.json')
            self.etl_job.export_to_json(self.test_contracts_data, json_path)
            
            assert os.path.exists(json_path)
            
            # Test Parquet export
            parquet_path = os.path.join(temp_dir, 'contracts.parquet')
            self.etl_job.export_to_parquet(self.test_contracts_data, parquet_path)
            
            assert os.path.exists(parquet_path)
    
    def test_incremental_processing(self):
        """Test incremental processing functionality"""
        # Create base data and new data
        base_data = self.test_contracts_data.iloc[:3]
        new_data = self.test_contracts_data.iloc[3:]
        
        # Test incremental merge
        merged_data = self.etl_job.merge_incremental_data(base_data, new_data, 'contract_id')
        
        assert len(merged_data) == len(self.test_contracts_data)
        assert len(merged_data['contract_id'].unique()) == len(self.test_contracts_data)
    
    def test_error_handling(self):
        """Test error handling functionality"""
        # Test with malformed data
        malformed_data = self.test_contracts_data.copy()
        malformed_data.loc[0, 'contract_value'] = 'invalid_value'
        
        # Should handle errors gracefully
        result = self.etl_job.process_with_error_handling(malformed_data)
        
        assert 'processed_data' in result
        assert 'errors' in result
        assert len(result['errors']) > 0
    
    def test_performance_monitoring(self):
        """Test performance monitoring"""
        performance_metrics = self.etl_job.monitor_performance(self.test_contracts_data)
        
        assert 'processing_time' in performance_metrics
        assert 'memory_usage' in performance_metrics
        assert 'record_count' in performance_metrics
        assert performance_metrics['record_count'] == len(self.test_contracts_data)
    
    def test_data_lineage_tracking(self):
        """Test data lineage tracking"""
        lineage_info = self.etl_job.track_data_lineage(
            source_data=self.test_contracts_data,
            transformations=['cleaning', 'enrichment', 'aggregation']
        )
        
        assert 'source_metadata' in lineage_info
        assert 'transformation_steps' in lineage_info
        assert 'output_metadata' in lineage_info
        assert len(lineage_info['transformation_steps']) == 3
    
    def test_comprehensive_etl_pipeline(self):
        """Test complete ETL pipeline execution"""
        pipeline_result = self.etl_job.run_pipeline(self.test_contracts_data)
        
        assert 'raw_data' in pipeline_result
        assert 'cleaned_data' in pipeline_result
        assert 'transformed_data' in pipeline_result
        assert 'enriched_data' in pipeline_result
        assert 'quality_report' in pipeline_result
        assert 'performance_metrics' in pipeline_result
        
        # Verify data integrity through pipeline
        assert len(pipeline_result['raw_data']) == len(pipeline_result['enriched_data'])
        assert pipeline_result['quality_report']['overall_score'] > 0.8
    
    def test_schema_validation(self):
        """Test schema validation"""
        expected_schema = {
            'contract_id': 'object',
            'client_name': 'object',
            'contract_value': 'int64',
            'start_date': 'object',
            'end_date': 'object',
            'status': 'object',
            'contract_type': 'object',
            'risk_level': 'object'
        }
        
        validation_result = self.etl_job.validate_schema(
            self.test_contracts_data, 
            expected_schema
        )
        
        assert validation_result['is_valid'] == True
        assert len(validation_result['schema_errors']) == 0
    
    def test_business_rules_validation(self):
        """Test business rules validation"""
        business_rules = {
            'contract_value_positive': lambda df: df['contract_value'] > 0,
            'start_date_before_end_date': lambda df: pd.to_datetime(df['start_date']) < pd.to_datetime(df['end_date']),
            'valid_status': lambda df: df['status'].isin(['Active', 'Pending', 'Completed', 'Terminated'])
        }
        
        validation_result = self.etl_job.validate_business_rules(
            self.test_contracts_data, 
            business_rules
        )
        
        assert validation_result['is_valid'] == True
        assert len(validation_result['rule_violations']) == 0
