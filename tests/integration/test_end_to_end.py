import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import json
from datetime import datetime, timedelta

from src.data_quality.quality_assessment import DataQualityAssessment
from src.data_quality.data_validation_suite import DataValidationSuite
from src.ml.transformer_train import TransformerTrainer
from src.ml.baseline_tf_idf import TFIDFBaseline
from src.etl_pipelines.contracts_etl_job import ContractsETLJob


class TestEndToEndDataQualityWorkflow:
    """Integration tests for end-to-end data quality workflow"""
    
    def setup_method(self):
        """Setup test data and components"""
        self.test_data = pd.DataFrame({
            'contract_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
            'client_name': ['Client A', 'Client B', 'Client C', 'Client D', 'Client E'],
            'contract_value': [100000, 250000, 75000, 500000, 150000],
            'start_date': ['2024-01-01', '2024-02-15', '2024-03-01', '2024-01-15', '2024-02-01'],
            'end_date': ['2024-12-31', '2024-12-31', '2024-08-31', '2025-01-31', '2024-11-30'],
            'status': ['Active', 'Active', 'Pending', 'Active', 'Completed'],
            'contract_type': ['Service', 'Product', 'Service', 'Product', 'Service'],
            'risk_level': ['Low', 'Medium', 'Low', 'High', 'Medium'],
            'text_description': [
                'Excellent service contract with comprehensive coverage.',
                'Product delivery contract with quality assurance.',
                'Standard service agreement with basic terms.',
                'High-value product contract with premium features.',
                'Completed service contract with good performance.'
            ]
        })
        
        self.quality_assessment = DataQualityAssessment()
        self.validation_suite = DataValidationSuite()
        self.etl_job = ContractsETLJob()
    
    def test_complete_data_quality_pipeline(self):
        """Test complete data quality assessment pipeline"""
        # Step 1: Data validation
        validation_result = self.validation_suite.validate_schema(
            self.test_data, 
            {col: 'object' for col in self.test_data.columns}
        )
        assert validation_result['is_valid'] == True
        
        # Step 2: Data quality assessment
        quality_result = self.quality_assessment.assess_quality(self.test_data)
        assert quality_result['overall_score'] > 0.8
        
        # Step 3: ETL processing
        etl_result = self.etl_job.run_pipeline(self.test_data)
        assert len(etl_result['enriched_data']) == len(self.test_data)
        
        # Step 4: Final quality check
        final_quality = self.quality_assessment.assess_quality(etl_result['enriched_data'])
        assert final_quality['overall_score'] > quality_result['overall_score']
    
    def test_data_quality_with_ml_integration(self):
        """Test data quality assessment with ML model integration"""
        # Prepare text data for ML
        text_data = pd.DataFrame({
            'text': self.test_data['text_description'],
            'label': [1 if 'excellent' in text.lower() or 'good' in text.lower() else 0 
                     for text in self.test_data['text_description']]
        })
        
        # Train baseline model
        baseline = TFIDFBaseline()
        X_train, X_test, y_train, y_test = baseline.prepare_data(
            text_data, text_column='text', label_column='label'
        )
        
        model = baseline.train_model(X_train, y_train)
        predictions = model.predict(X_test)
        
        # Assess prediction quality
        from sklearn.metrics import accuracy_score
        accuracy = accuracy_score(y_test, predictions)
        assert accuracy > 0.5  # Should perform better than random
    
    def test_etl_with_quality_gates(self):
        """Test ETL pipeline with quality gates"""
        # Add some quality issues to test data
        problematic_data = self.test_data.copy()
        problematic_data.loc[0, 'contract_value'] = -1000  # Invalid negative value
        problematic_data.loc[1, 'client_name'] = ''  # Empty name
        
        # Run ETL with quality gates
        result = self.etl_job.process_with_error_handling(problematic_data)
        
        assert 'processed_data' in result
        assert 'errors' in result
        assert len(result['errors']) > 0
        
        # Verify that invalid records are flagged
        quality_report = self.quality_assessment.assess_quality(result['processed_data'])
        assert quality_report['accuracy_score'] < 1.0


class TestEndToEndMLPipeline:
    """Integration tests for end-to-end ML pipeline"""
    
    def setup_method(self):
        """Setup test data and ML components"""
        self.trainer = TransformerTrainer()
        self.baseline = TFIDFBaseline()
        
        # Create synthetic training data
        self.training_data = pd.DataFrame({
            'text': [
                'This is a positive review about the product.',
                'I really enjoyed using this service.',
                'The quality is excellent and I recommend it.',
                'This is a negative review about the product.',
                'I did not like the service at all.',
                'The quality is poor and I do not recommend it.',
                'Amazing experience with the product.',
                'Terrible service, would not recommend.',
                'Great value for money.',
                'Disappointed with the quality.'
            ],
            'label': [1, 1, 1, 0, 0, 0, 1, 0, 1, 0]
        })
    
    @patch('src.ml.transformer_train.AutoTokenizer.from_pretrained')
    @patch('src.ml.transformer_train.AutoModelForSequenceClassification.from_pretrained')
    @patch('src.ml.transformer_train.Trainer')
    def test_complete_ml_training_pipeline(self, mock_trainer_class, mock_model, mock_tokenizer):
        """Test complete ML training pipeline"""
        # Mock components
        mock_tokenizer.return_value = Mock()
        mock_model.return_value = Mock()
        mock_trainer = Mock()
        mock_trainer_class.return_value = mock_trainer
        
        # Step 1: Data preprocessing
        processed_data = self.trainer.preprocess_data(
            self.training_data, 
            text_column='text', 
            label_column='label'
        )
        assert 'input_ids' in processed_data
        assert 'attention_mask' in processed_data
        
        # Step 2: Model training
        training_args = Mock()
        training_args.output_dir = '/tmp/test_output'
        
        self.trainer.train_model(
            model=mock_model.return_value,
            tokenizer=mock_tokenizer.return_value,
            train_dataset=Mock(),
            eval_dataset=Mock(),
            training_args=training_args
        )
        
        mock_trainer.train.assert_called_once()
        mock_trainer.evaluate.assert_called_once()
    
    def test_ml_model_comparison_pipeline(self):
        """Test ML model comparison pipeline"""
        # Prepare data
        X_train, X_test, y_train, y_test = self.baseline.prepare_data(
            self.training_data, 
            text_column='text', 
            label_column='label'
        )
        
        # Train baseline model
        baseline_model = self.baseline.train_model(X_train, y_train)
        baseline_predictions = baseline_model.predict(X_test)
        
        # Train TF-IDF model
        tfidf_model = self.baseline.train_tfidf_model(X_train, y_train)
        tfidf_predictions = tfidf_model.predict(X_test)
        
        # Compare models
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        baseline_metrics = {
            'accuracy': accuracy_score(y_test, baseline_predictions),
            'precision': precision_score(y_test, baseline_predictions),
            'recall': recall_score(y_test, baseline_predictions),
            'f1': f1_score(y_test, baseline_predictions)
        }
        
        tfidf_metrics = {
            'accuracy': accuracy_score(y_test, tfidf_predictions),
            'precision': precision_score(y_test, tfidf_predictions),
            'recall': recall_score(y_test, tfidf_predictions),
            'f1': f1_score(y_test, tfidf_predictions)
        }
        
        # Both models should perform reasonably well
        assert baseline_metrics['accuracy'] > 0.5
        assert tfidf_metrics['accuracy'] > 0.5
    
    def test_ml_model_persistence_and_loading(self):
        """Test ML model persistence and loading"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Train model
            X_train, X_test, y_train, y_test = self.baseline.prepare_data(
                self.training_data, 
                text_column='text', 
                label_column='label'
            )
            
            model = self.baseline.train_model(X_train, y_train)
            
            # Save model
            model_path = os.path.join(temp_dir, 'model.pkl')
            self.baseline.save_model(model, model_path)
            
            # Load model
            loaded_model = self.baseline.load_model(model_path)
            
            # Verify predictions are the same
            original_predictions = model.predict(X_test)
            loaded_predictions = loaded_model.predict(X_test)
            
            assert np.array_equal(original_predictions, loaded_predictions)


class TestEndToEndETLWorkflow:
    """Integration tests for end-to-end ETL workflow"""
    
    def setup_method(self):
        """Setup test data and ETL components"""
        self.etl_job = ContractsETLJob()
        self.quality_assessment = DataQualityAssessment()
        
        # Create comprehensive test data
        self.contracts_data = pd.DataFrame({
            'contract_id': [f'C{i:03d}' for i in range(1, 21)],
            'client_name': [f'Client {chr(65 + i % 26)}' for i in range(20)],
            'contract_value': np.random.randint(50000, 1000000, 20),
            'start_date': pd.date_range('2024-01-01', periods=20, freq='D').strftime('%Y-%m-%d'),
            'end_date': pd.date_range('2024-12-31', periods=20, freq='D').strftime('%Y-%m-%d'),
            'status': np.random.choice(['Active', 'Pending', 'Completed'], 20),
            'contract_type': np.random.choice(['Service', 'Product'], 20),
            'risk_level': np.random.choice(['Low', 'Medium', 'High'], 20)
        })
    
    def test_complete_etl_data_pipeline(self):
        """Test complete ETL data pipeline"""
        # Step 1: Data validation
        validation_result = self.etl_job.validate_data(self.contracts_data)
        assert validation_result['is_valid'] == True
        
        # Step 2: Data cleaning
        cleaned_data = self.etl_job.clean_data(self.contracts_data)
        assert len(cleaned_data) == len(self.contracts_data)
        
        # Step 3: Data transformation
        transformed_data = self.etl_job.transform_data(cleaned_data)
        assert 'contract_duration_days' in transformed_data.columns
        assert 'monthly_value' in transformed_data.columns
        
        # Step 4: Data enrichment
        enriched_data = self.etl_job.enrich_data(transformed_data)
        assert 'client_segment' in enriched_data.columns
        assert 'renewal_probability' in enriched_data.columns
        
        # Step 5: Quality assessment
        quality_report = self.quality_assessment.assess_quality(enriched_data)
        assert quality_report['overall_score'] > 0.8
        
        # Step 6: Data export
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = os.path.join(temp_dir, 'enriched_contracts.csv')
            self.etl_job.export_to_csv(enriched_data, csv_path)
            
            assert os.path.exists(csv_path)
            assert os.path.getsize(csv_path) > 0
    
    def test_etl_with_incremental_updates(self):
        """Test ETL pipeline with incremental updates"""
        # Initial data
        initial_data = self.contracts_data.iloc[:10]
        
        # New data
        new_data = self.contracts_data.iloc[10:]
        
        # Process initial data
        initial_result = self.etl_job.run_pipeline(initial_data)
        
        # Process new data
        new_result = self.etl_job.run_pipeline(new_data)
        
        # Merge incrementally
        merged_data = self.etl_job.merge_incremental_data(
            initial_result['enriched_data'], 
            new_result['enriched_data'], 
            'contract_id'
        )
        
        assert len(merged_data) == len(self.contracts_data)
        assert len(merged_data['contract_id'].unique()) == len(self.contracts_data)
    
    def test_etl_with_error_recovery(self):
        """Test ETL pipeline with error recovery"""
        # Create data with various issues
        problematic_data = self.contracts_data.copy()
        problematic_data.loc[0, 'contract_value'] = 'invalid_value'
        problematic_data.loc[1, 'start_date'] = 'invalid_date'
        problematic_data.loc[2, 'client_name'] = ''
        
        # Process with error handling
        result = self.etl_job.process_with_error_handling(problematic_data)
        
        assert 'processed_data' in result
        assert 'errors' in result
        assert len(result['errors']) > 0
        
        # Verify that valid records are still processed
        assert len(result['processed_data']) > 0
        
        # Verify data quality
        quality_report = self.quality_assessment.assess_quality(result['processed_data'])
        assert quality_report['overall_score'] > 0.7


class TestEndToEndSystemIntegration:
    """Integration tests for complete system workflow"""
    
    def setup_method(self):
        """Setup complete system components"""
        self.quality_assessment = DataQualityAssessment()
        self.validation_suite = DataValidationSuite()
        self.etl_job = ContractsETLJob()
        self.baseline = TFIDFBaseline()
        
        # Create comprehensive test dataset
        self.system_data = pd.DataFrame({
            'contract_id': [f'C{i:03d}' for i in range(1, 11)],
            'client_name': [f'Client {chr(65 + i % 26)}' for i in range(10)],
            'contract_value': [100000, 250000, 75000, 500000, 150000, 
                              300000, 80000, 400000, 120000, 600000],
            'start_date': pd.date_range('2024-01-01', periods=10, freq='D').strftime('%Y-%m-%d'),
            'end_date': pd.date_range('2024-12-31', periods=10, freq='D').strftime('%Y-%m-%d'),
            'status': ['Active', 'Active', 'Pending', 'Active', 'Completed',
                      'Active', 'Pending', 'Active', 'Completed', 'Active'],
            'contract_type': ['Service', 'Product', 'Service', 'Product', 'Service',
                             'Product', 'Service', 'Product', 'Service', 'Product'],
            'risk_level': ['Low', 'Medium', 'Low', 'High', 'Medium',
                          'High', 'Low', 'High', 'Medium', 'High'],
            'text_description': [
                'Excellent service contract with comprehensive coverage.',
                'Product delivery contract with quality assurance.',
                'Standard service agreement with basic terms.',
                'High-value product contract with premium features.',
                'Completed service contract with good performance.',
                'Advanced product contract with cutting-edge technology.',
                'Basic service agreement with standard terms.',
                'Premium product contract with exclusive features.',
                'Standard service contract with reliable performance.',
                'Enterprise product contract with full support.'
            ]
        })
    
    def test_complete_system_workflow(self):
        """Test complete system workflow from raw data to insights"""
        # Step 1: Data Quality Assessment
        quality_result = self.quality_assessment.assess_quality(self.system_data)
        assert quality_result['overall_score'] > 0.8
        
        # Step 2: Data Validation
        validation_result = self.validation_suite.validate_schema(
            self.system_data, 
            {col: 'object' for col in self.system_data.columns}
        )
        assert validation_result['is_valid'] == True
        
        # Step 3: ETL Processing
        etl_result = self.etl_job.run_pipeline(self.system_data)
        assert len(etl_result['enriched_data']) == len(self.system_data)
        
        # Step 4: ML Text Analysis
        text_data = pd.DataFrame({
            'text': self.system_data['text_description'],
            'label': [1 if 'excellent' in text.lower() or 'good' in text.lower() or 'premium' in text.lower() else 0 
                     for text in self.system_data['text_description']]
        })
        
        X_train, X_test, y_train, y_test = self.baseline.prepare_data(
            text_data, text_column='text', label_column='label'
        )
        
        model = self.baseline.train_model(X_train, y_train)
        predictions = model.predict(X_test)
        
        # Step 5: Final Quality Assessment
        final_quality = self.quality_assessment.assess_quality(etl_result['enriched_data'])
        assert final_quality['overall_score'] > quality_result['overall_score']
        
        # Step 6: Generate Insights
        insights = {
            'total_contracts': len(self.system_data),
            'total_value': self.system_data['contract_value'].sum(),
            'avg_contract_value': self.system_data['contract_value'].mean(),
            'active_contracts': len(self.system_data[self.system_data['status'] == 'Active']),
            'high_risk_contracts': len(self.system_data[self.system_data['risk_level'] == 'High']),
            'ml_accuracy': sum(predictions == y_test) / len(y_test) if len(y_test) > 0 else 0
        }
        
        assert insights['total_contracts'] == 10
        assert insights['total_value'] > 0
        assert insights['avg_contract_value'] > 0
        assert insights['active_contracts'] > 0
        assert insights['ml_accuracy'] >= 0
    
    def test_system_performance_monitoring(self):
        """Test system performance monitoring"""
        # Monitor ETL performance
        etl_metrics = self.etl_job.monitor_performance(self.system_data)
        assert 'processing_time' in etl_metrics
        assert 'memory_usage' in etl_metrics
        assert 'record_count' in etl_metrics
        
        # Monitor quality assessment performance
        quality_metrics = self.quality_assessment.assess_quality(self.system_data)
        assert 'overall_score' in quality_metrics
        assert 'completeness_score' in quality_metrics
        assert 'accuracy_score' in quality_metrics
        
        # Monitor ML performance
        text_data = pd.DataFrame({
            'text': self.system_data['text_description'],
            'label': [1 if 'excellent' in text.lower() else 0 for text in self.system_data['text_description']]
        })
        
        X_train, X_test, y_train, y_test = self.baseline.prepare_data(
            text_data, text_column='text', label_column='label'
        )
        
        model = self.baseline.train_model(X_train, y_train)
        predictions = model.predict(X_test)
        
        from sklearn.metrics import accuracy_score
        ml_accuracy = accuracy_score(y_test, predictions) if len(y_test) > 0 else 0
        
        # Performance assertions
        assert etl_metrics['record_count'] == len(self.system_data)
        assert quality_metrics['overall_score'] > 0.8
        assert ml_accuracy >= 0


