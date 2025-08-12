import pytest
import pandas as pd
import numpy as np
import time
import psutil
import os
from unittest.mock import Mock, patch
import tempfile
import json

from src.data_quality.quality_assessment import DataQualityAssessment
from src.etl_pipelines.contracts_etl_job import ContractsETLJob
from src.ml.baseline_tf_idf import TFIDFBaseline


class TestDataQualityPerformance:
    """Performance tests for data quality components"""
    
    def setup_method(self):
        """Setup test data and components"""
        self.quality_assessment = DataQualityAssessment()
        self.etl_job = ContractsETLJob()
        
        # Generate large datasets for performance testing
        np.random.seed(42)
    
    def generate_large_dataset(self, n_records):
        """Generate large dataset for performance testing"""
        return pd.DataFrame({
            'contract_id': [f'C{i:06d}' for i in range(1, n_records + 1)],
            'client_name': [f'Client {chr(65 + i % 26)}' for i in range(n_records)],
            'contract_value': np.random.randint(50000, 1000000, n_records),
            'start_date': pd.date_range('2024-01-01', periods=n_records, freq='D').strftime('%Y-%m-%d'),
            'end_date': pd.date_range('2024-12-31', periods=n_records, freq='D').strftime('%Y-%m-%d'),
            'status': np.random.choice(['Active', 'Pending', 'Completed'], n_records),
            'contract_type': np.random.choice(['Service', 'Product'], n_records),
            'risk_level': np.random.choice(['Low', 'Medium', 'High'], n_records),
            'text_description': [
                f'Contract description for contract {i} with various details and specifications.'
                for i in range(1, n_records + 1)
            ]
        })
    
    def measure_memory_usage(self):
        """Measure current memory usage"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    def measure_execution_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start_time = time.time()
        start_memory = self.measure_memory_usage()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = self.measure_memory_usage()
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        return result, execution_time, memory_usage
    
    @pytest.mark.performance
    def test_quality_assessment_performance_scaling(self):
        """Test quality assessment performance with different dataset sizes"""
        dataset_sizes = [100, 1000, 10000, 50000]
        performance_results = {}
        
        for size in dataset_sizes:
            print(f"\nTesting with {size:,} records...")
            
            # Generate dataset
            data = self.generate_large_dataset(size)
            
            # Measure quality assessment performance
            result, execution_time, memory_usage = self.measure_execution_time(
                self.quality_assessment.assess_quality, data
            )
            
            performance_results[size] = {
                'execution_time': execution_time,
                'memory_usage': memory_usage,
                'quality_score': result['overall_score']
            }
            
            print(f"  Execution time: {execution_time:.2f}s")
            print(f"  Memory usage: {memory_usage:.2f}MB")
            print(f"  Quality score: {result['overall_score']:.3f}")
            
            # Performance assertions
            assert execution_time < 60, f"Quality assessment took too long: {execution_time:.2f}s"
            assert memory_usage < 2048, f"Memory usage too high: {memory_usage:.2f}MB"
            assert result['overall_score'] > 0.8, f"Quality score too low: {result['overall_score']:.3f}"
        
        # Verify performance scaling (should be roughly linear)
        times = [performance_results[size]['execution_time'] for size in dataset_sizes]
        assert times[-1] < times[0] * 100, "Performance scaling is not reasonable"
    
    @pytest.mark.performance
    def test_etl_pipeline_performance(self):
        """Test ETL pipeline performance with large datasets"""
        dataset_sizes = [1000, 10000, 50000]
        performance_results = {}
        
        for size in dataset_sizes:
            print(f"\nTesting ETL pipeline with {size:,} records...")
            
            # Generate dataset
            data = self.generate_large_dataset(size)
            
            # Measure ETL pipeline performance
            result, execution_time, memory_usage = self.measure_execution_time(
                self.etl_job.run_pipeline, data
            )
            
            performance_results[size] = {
                'execution_time': execution_time,
                'memory_usage': memory_usage,
                'output_records': len(result['enriched_data'])
            }
            
            print(f"  Execution time: {execution_time:.2f}s")
            print(f"  Memory usage: {memory_usage:.2f}MB")
            print(f"  Output records: {result['enriched_data'].shape[0]:,}")
            
            # Performance assertions
            assert execution_time < 120, f"ETL pipeline took too long: {execution_time:.2f}s"
            assert memory_usage < 4096, f"Memory usage too high: {memory_usage:.2f}MB"
            assert len(result['enriched_data']) == size, "Output record count mismatch"
    
    @pytest.mark.performance
    def test_data_validation_performance(self):
        """Test data validation performance with large datasets"""
        dataset_sizes = [1000, 10000, 50000]
        performance_results = {}
        
        for size in dataset_sizes:
            print(f"\nTesting data validation with {size:,} records...")
            
            # Generate dataset
            data = self.generate_large_dataset(size)
            
            # Define validation rules
            schema = {col: 'object' for col in data.columns}
            constraints = {
                'contract_value': {'min': 0, 'max': 10000000},
                'start_date': {'format': 'date'},
                'end_date': {'format': 'date'}
            }
            
            # Measure validation performance
            result, execution_time, memory_usage = self.measure_execution_time(
                self.etl_job.validate_data, data
            )
            
            performance_results[size] = {
                'execution_time': execution_time,
                'memory_usage': memory_usage,
                'is_valid': result['is_valid']
            }
            
            print(f"  Execution time: {execution_time:.2f}s")
            print(f"  Memory usage: {memory_usage:.2f}MB")
            print(f"  Is valid: {result['is_valid']}")
            
            # Performance assertions
            assert execution_time < 30, f"Data validation took too long: {execution_time:.2f}s"
            assert memory_usage < 1024, f"Memory usage too high: {memory_usage:.2f}MB"
            assert result['is_valid'] == True, "Data should be valid"


class TestMLPerformance:
    """Performance tests for ML components"""
    
    def setup_method(self):
        """Setup ML components"""
        self.baseline = TFIDFBaseline()
        
        # Generate large text datasets
        np.random.seed(42)
    
    def generate_large_text_dataset(self, n_records):
        """Generate large text dataset for ML performance testing"""
        positive_texts = [
            'Excellent service with outstanding quality and great performance.',
            'Amazing product that exceeds expectations and delivers value.',
            'Outstanding experience with premium features and top-notch support.',
            'Fantastic service with excellent results and superior quality.',
            'Wonderful product with exceptional performance and great value.'
        ]
        
        negative_texts = [
            'Poor service with terrible quality and disappointing performance.',
            'Awful product that fails to meet expectations and lacks value.',
            'Terrible experience with basic features and poor support.',
            'Horrible service with bad results and inferior quality.',
            'Dreadful product with poor performance and no value.'
        ]
        
        texts = []
        labels = []
        
        for i in range(n_records):
            if np.random.random() > 0.5:
                text = np.random.choice(positive_texts) + f' Contract {i+1}.'
                label = 1
            else:
                text = np.random.choice(negative_texts) + f' Contract {i+1}.'
                label = 0
            
            texts.append(text)
            labels.append(label)
        
        return pd.DataFrame({
            'text': texts,
            'label': labels
        })
    
    @pytest.mark.performance
    def test_ml_training_performance(self):
        """Test ML model training performance with different dataset sizes"""
        dataset_sizes = [100, 1000, 5000, 10000]
        performance_results = {}
        
        for size in dataset_sizes:
            print(f"\nTesting ML training with {size:,} records...")
            
            # Generate dataset
            data = self.generate_large_text_dataset(size)
            
            # Prepare data
            start_time = time.time()
            X_train, X_test, y_train, y_test = self.baseline.prepare_data(
                data, text_column='text', label_column='label'
            )
            prep_time = time.time() - start_time
            
            # Measure training performance
            start_time = time.time()
            start_memory = self.measure_memory_usage()
            
            model = self.baseline.train_model(X_train, y_train)
            
            end_time = time.time()
            end_memory = self.measure_memory_usage()
            
            training_time = end_time - start_time
            memory_usage = end_memory - start_memory
            
            # Measure prediction performance
            pred_start_time = time.time()
            predictions = model.predict(X_test)
            pred_time = time.time() - pred_start_time
            
            performance_results[size] = {
                'prep_time': prep_time,
                'training_time': training_time,
                'prediction_time': pred_time,
                'memory_usage': memory_usage,
                'test_size': len(X_test)
            }
            
            print(f"  Data prep time: {prep_time:.2f}s")
            print(f"  Training time: {training_time:.2f}s")
            print(f"  Prediction time: {pred_time:.2f}s")
            print(f"  Memory usage: {memory_usage:.2f}MB")
            print(f"  Test set size: {len(X_test):,}")
            
            # Performance assertions
            assert prep_time < 60, f"Data preparation took too long: {prep_time:.2f}s"
            assert training_time < 300, f"Training took too long: {training_time:.2f}s"
            assert pred_time < 10, f"Prediction took too long: {pred_time:.2f}s"
            assert memory_usage < 2048, f"Memory usage too high: {memory_usage:.2f}MB"
    
    @pytest.mark.performance
    def test_feature_extraction_performance(self):
        """Test feature extraction performance"""
        dataset_sizes = [100, 1000, 5000, 10000]
        performance_results = {}
        
        for size in dataset_sizes:
            print(f"\nTesting feature extraction with {size:,} records...")
            
            # Generate dataset
            data = self.generate_large_text_dataset(size)
            
            # Measure feature extraction performance
            result, execution_time, memory_usage = self.measure_execution_time(
                self.baseline.extract_features, data['text']
            )
            
            performance_results[size] = {
                'execution_time': execution_time,
                'memory_usage': memory_usage,
                'feature_count': result.shape[1] if hasattr(result, 'shape') else 0
            }
            
            print(f"  Execution time: {execution_time:.2f}s")
            print(f"  Memory usage: {memory_usage:.2f}MB")
            print(f"  Feature count: {result.shape[1] if hasattr(result, 'shape') else 0}")
            
            # Performance assertions
            assert execution_time < 120, f"Feature extraction took too long: {execution_time:.2f}s"
            assert memory_usage < 2048, f"Memory usage too high: {memory_usage:.2f}MB"


class TestSystemPerformance:
    """System-wide performance tests"""
    
    def setup_method(self):
        """Setup system components"""
        self.quality_assessment = DataQualityAssessment()
        self.etl_job = ContractsETLJob()
        self.baseline = TFIDFBaseline()
    
    def measure_memory_usage(self):
        """Measure current memory usage"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    def measure_execution_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start_time = time.time()
        start_memory = self.measure_memory_usage()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = self.measure_memory_usage()
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        return result, execution_time, memory_usage
    
    def generate_comprehensive_dataset(self, n_records):
        """Generate comprehensive dataset for system testing"""
        np.random.seed(42)
        
        return pd.DataFrame({
            'contract_id': [f'C{i:06d}' for i in range(1, n_records + 1)],
            'client_name': [f'Client {chr(65 + i % 26)}' for i in range(n_records)],
            'contract_value': np.random.randint(50000, 1000000, n_records),
            'start_date': pd.date_range('2024-01-01', periods=n_records, freq='D').strftime('%Y-%m-%d'),
            'end_date': pd.date_range('2024-12-31', periods=n_records, freq='D').strftime('%Y-%m-%d'),
            'status': np.random.choice(['Active', 'Pending', 'Completed'], n_records),
            'contract_type': np.random.choice(['Service', 'Product'], n_records),
            'risk_level': np.random.choice(['Low', 'Medium', 'High'], n_records),
            'text_description': [
                f'Contract description for contract {i} with various details and specifications.'
                for i in range(1, n_records + 1)
            ]
        })
    
    @pytest.mark.performance
    def test_end_to_end_system_performance(self):
        """Test end-to-end system performance"""
        dataset_sizes = [1000, 10000, 50000]
        performance_results = {}
        
        for size in dataset_sizes:
            print(f"\nTesting end-to-end system with {size:,} records...")
            
            # Generate dataset
            data = self.generate_comprehensive_dataset(size)
            
            # Step 1: Data Quality Assessment
            print("  Step 1: Data Quality Assessment")
            quality_result, quality_time, quality_memory = self.measure_execution_time(
                self.quality_assessment.assess_quality, data
            )
            
            # Step 2: ETL Processing
            print("  Step 2: ETL Processing")
            etl_result, etl_time, etl_memory = self.measure_execution_time(
                self.etl_job.run_pipeline, data
            )
            
            # Step 3: ML Text Analysis (sample subset for performance)
            print("  Step 3: ML Text Analysis")
            text_sample = data.head(min(1000, len(data)))
            text_data = pd.DataFrame({
                'text': text_sample['text_description'],
                'label': [1 if 'excellent' in text.lower() or 'good' in text.lower() else 0 
                         for text in text_sample['text_description']]
            })
            
            X_train, X_test, y_train, y_test = self.baseline.prepare_data(
                text_data, text_column='text', label_column='label'
            )
            
            ml_result, ml_time, ml_memory = self.measure_execution_time(
                self.baseline.train_model, X_train, y_train
            )
            
            # Calculate total performance
            total_time = quality_time + etl_time + ml_time
            total_memory = max(quality_memory, etl_memory, ml_memory)
            
            performance_results[size] = {
                'quality_time': quality_time,
                'etl_time': etl_time,
                'ml_time': ml_time,
                'total_time': total_time,
                'total_memory': total_memory,
                'quality_score': quality_result['overall_score']
            }
            
            print(f"  Quality assessment: {quality_time:.2f}s, {quality_memory:.2f}MB")
            print(f"  ETL processing: {etl_time:.2f}s, {etl_memory:.2f}MB")
            print(f"  ML analysis: {ml_time:.2f}s, {ml_memory:.2f}MB")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Peak memory: {total_memory:.2f}MB")
            print(f"  Quality score: {quality_result['overall_score']:.3f}")
            
            # Performance assertions
            assert total_time < 600, f"Total processing time too long: {total_time:.2f}s"
            assert total_memory < 8192, f"Peak memory usage too high: {total_memory:.2f}MB"
            assert quality_result['overall_score'] > 0.8, f"Quality score too low: {quality_result['overall_score']:.3f}"
    
    @pytest.mark.performance
    def test_concurrent_processing_performance(self):
        """Test performance under concurrent processing scenarios"""
        import concurrent.futures
        import threading
        
        # Generate multiple datasets
        datasets = []
        for i in range(5):
            data = self.generate_comprehensive_dataset(1000)
            datasets.append(data)
        
        print(f"\nTesting concurrent processing with 5 datasets of 1,000 records each...")
        
        # Process datasets concurrently
        start_time = time.time()
        start_memory = self.measure_memory_usage()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit quality assessment tasks
            quality_futures = [
                executor.submit(self.quality_assessment.assess_quality, data)
                for data in datasets
            ]
            
            # Submit ETL tasks
            etl_futures = [
                executor.submit(self.etl_job.run_pipeline, data)
                for data in datasets
            ]
            
            # Collect results
            quality_results = [future.result() for future in quality_futures]
            etl_results = [future.result() for future in etl_futures]
        
        end_time = time.time()
        end_memory = self.measure_memory_usage()
        
        total_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        print(f"  Concurrent processing time: {total_time:.2f}s")
        print(f"  Memory usage: {memory_usage:.2f}MB")
        print(f"  Quality results: {len(quality_results)}")
        print(f"  ETL results: {len(etl_results)}")
        
        # Performance assertions
        assert total_time < 300, f"Concurrent processing took too long: {total_time:.2f}s"
        assert memory_usage < 4096, f"Memory usage too high: {memory_usage:.2f}MB"
        assert len(quality_results) == 5, "Not all quality assessments completed"
        assert len(etl_results) == 5, "Not all ETL processes completed"
    
    @pytest.mark.performance
    def test_memory_efficiency(self):
        """Test memory efficiency with large datasets"""
        dataset_sizes = [10000, 50000, 100000]
        memory_results = {}
        
        for size in dataset_sizes:
            print(f"\nTesting memory efficiency with {size:,} records...")
            
            # Generate dataset
            data = self.generate_comprehensive_dataset(size)
            
            # Measure memory usage at different stages
            initial_memory = self.measure_memory_usage()
            
            # Quality assessment
            quality_result, _, quality_memory = self.measure_execution_time(
                self.quality_assessment.assess_quality, data
            )
            
            # ETL processing
            etl_result, _, etl_memory = self.measure_execution_time(
                self.etl_job.run_pipeline, data
            )
            
            # Final memory
            final_memory = self.measure_memory_usage()
            
            memory_results[size] = {
                'initial_memory': initial_memory,
                'quality_memory': quality_memory,
                'etl_memory': etl_memory,
                'final_memory': final_memory,
                'peak_memory': max(initial_memory, quality_memory, etl_memory, final_memory)
            }
            
            print(f"  Initial memory: {initial_memory:.2f}MB")
            print(f"  Quality assessment memory: {quality_memory:.2f}MB")
            print(f"  ETL memory: {etl_memory:.2f}MB")
            print(f"  Final memory: {final_memory:.2f}MB")
            print(f"  Peak memory: {memory_results[size]['peak_memory']:.2f}MB")
            
            # Memory efficiency assertions
            assert memory_results[size]['peak_memory'] < 8192, f"Peak memory too high: {memory_results[size]['peak_memory']:.2f}MB"
            assert final_memory < initial_memory * 2, "Memory not properly released"
    
    @pytest.mark.performance
    def test_throughput_performance(self):
        """Test system throughput performance"""
        # Test with continuous data processing
        batch_size = 1000
        num_batches = 10
        total_records = batch_size * num_batches
        
        print(f"\nTesting throughput with {total_records:,} records in {num_batches} batches...")
        
        start_time = time.time()
        start_memory = self.measure_memory_usage()
        
        processed_batches = 0
        total_quality_score = 0
        
        for i in range(num_batches):
            # Generate batch
            batch_data = self.generate_comprehensive_dataset(batch_size)
            
            # Process batch
            quality_result = self.quality_assessment.assess_quality(batch_data)
            etl_result = self.etl_job.run_pipeline(batch_data)
            
            processed_batches += 1
            total_quality_score += quality_result['overall_score']
            
            print(f"  Batch {i+1}/{num_batches} processed")
        
        end_time = time.time()
        end_memory = self.measure_memory_usage()
        
        total_time = end_time - start_time
        memory_usage = end_memory - start_memory
        avg_quality_score = total_quality_score / num_batches
        throughput = total_records / total_time
        
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Memory usage: {memory_usage:.2f}MB")
        print(f"  Average quality score: {avg_quality_score:.3f}")
        print(f"  Throughput: {throughput:.0f} records/second")
        
        # Throughput assertions
        assert total_time < 600, f"Total processing time too long: {total_time:.2f}s"
        assert throughput > 100, f"Throughput too low: {throughput:.0f} records/second"
        assert avg_quality_score > 0.8, f"Average quality score too low: {avg_quality_score:.3f}"
        assert memory_usage < 4096, f"Memory usage too high: {memory_usage:.2f}MB"


