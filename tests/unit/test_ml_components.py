import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import json

from src.ml.transformer_train import TransformerTrainer
from src.ml.baseline_tf_idf import TFIDFBaseline
from src.ml.eval_report import EvaluationReport
from src.ml.mlflow_utils import MLflowUtils


class TestTransformerTrainer:
    """Unit tests for TransformerTrainer"""
    
    def setup_method(self):
        """Setup test data"""
        self.trainer = TransformerTrainer()
        self.test_data = pd.DataFrame({
            'text': [
                'This is a positive review about the product.',
                'I really enjoyed using this service.',
                'The quality is excellent and I recommend it.',
                'This is a negative review about the product.',
                'I did not like the service at all.',
                'The quality is poor and I do not recommend it.'
            ],
            'label': [1, 1, 1, 0, 0, 0]
        })
    
    @patch('src.ml.transformer_train.AutoTokenizer.from_pretrained')
    @patch('src.ml.transformer_train.AutoModelForSequenceClassification.from_pretrained')
    def test_model_initialization(self, mock_model, mock_tokenizer):
        """Test model initialization"""
        mock_tokenizer.return_value = Mock()
        mock_model.return_value = Mock()
        
        model, tokenizer = self.trainer.initialize_model('bert-base-uncased', num_labels=2)
        
        assert model is not None
        assert tokenizer is not None
        mock_tokenizer.assert_called_once_with('bert-base-uncased')
        mock_model.assert_called_once()
    
    def test_data_preprocessing(self):
        """Test data preprocessing"""
        processed_data = self.trainer.preprocess_data(
            self.test_data, 
            text_column='text', 
            label_column='label'
        )
        
        assert 'input_ids' in processed_data
        assert 'attention_mask' in processed_data
        assert 'labels' in processed_data
        assert len(processed_data['input_ids']) == len(self.test_data)
    
    @patch('src.ml.transformer_train.Trainer')
    def test_model_training(self, mock_trainer_class):
        """Test model training"""
        mock_trainer = Mock()
        mock_trainer_class.return_value = mock_trainer
        
        # Mock training arguments
        training_args = Mock()
        training_args.output_dir = '/tmp/test_output'
        
        self.trainer.train_model(
            model=Mock(),
            tokenizer=Mock(),
            train_dataset=Mock(),
            eval_dataset=Mock(),
            training_args=training_args
        )
        
        mock_trainer.train.assert_called_once()
        mock_trainer.evaluate.assert_called_once()
    
    def test_hyperparameter_optimization(self):
        """Test hyperparameter optimization"""
        with patch('src.ml.transformer_train.Optuna') as mock_optuna:
            mock_study = Mock()
            mock_optuna.create_study.return_value = mock_study
            mock_study.optimize.return_value = None
            
            best_params = self.trainer.optimize_hyperparameters(
                train_dataset=Mock(),
                eval_dataset=Mock(),
                n_trials=5
            )
            
            assert isinstance(best_params, dict)
            mock_study.optimize.assert_called_once()
    
    def test_model_evaluation(self):
        """Test model evaluation"""
        mock_model = Mock()
        mock_dataset = Mock()
        
        # Mock predictions
        mock_model.return_value = Mock()
        mock_model.return_value.logits = np.random.randn(10, 2)
        
        metrics = self.trainer.evaluate_model(mock_model, mock_dataset)
        
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1' in metrics
    
    def test_model_saving_and_loading(self):
        """Test model saving and loading"""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_model = Mock()
            mock_tokenizer = Mock()
            
            # Test saving
            self.trainer.save_model(mock_model, mock_tokenizer, temp_dir)
            
            # Test loading
            loaded_model, loaded_tokenizer = self.trainer.load_model(temp_dir)
            
            assert loaded_model is not None
            assert loaded_tokenizer is not None


class TestTFIDFBaseline:
    """Unit tests for TFIDFBaseline"""
    
    def setup_method(self):
        """Setup test data"""
        self.baseline = TFIDFBaseline()
        self.test_data = pd.DataFrame({
            'text': [
                'This is a positive review about the product.',
                'I really enjoyed using this service.',
                'The quality is excellent and I recommend it.',
                'This is a negative review about the product.',
                'I did not like the service at all.',
                'The quality is poor and I do not recommend it.'
            ],
            'label': [1, 1, 1, 0, 0, 0]
        })
    
    def test_tfidf_vectorization(self):
        """Test TF-IDF vectorization"""
        X_train, X_test, y_train, y_test = self.baseline.prepare_data(
            self.test_data, 
            text_column='text', 
            label_column='label',
            test_size=0.3
        )
        
        # Train TF-IDF model
        tfidf_model = self.baseline.train_tfidf_model(X_train, y_train)
        
        assert tfidf_model is not None
        assert hasattr(tfidf_model, 'predict')
    
    def test_feature_extraction(self):
        """Test feature extraction"""
        features = self.baseline.extract_features(self.test_data['text'])
        
        assert isinstance(features, np.ndarray)
        assert features.shape[0] == len(self.test_data)
        assert features.shape[1] > 0  # Should have features
    
    def test_model_training(self):
        """Test baseline model training"""
        X_train, X_test, y_train, y_test = self.baseline.prepare_data(
            self.test_data, 
            text_column='text', 
            label_column='label'
        )
        
        model = self.baseline.train_model(X_train, y_train)
        
        assert model is not None
        assert hasattr(model, 'predict')
        assert hasattr(model, 'predict_proba')
    
    def test_model_evaluation(self):
        """Test baseline model evaluation"""
        X_train, X_test, y_train, y_test = self.baseline.prepare_data(
            self.test_data, 
            text_column='text', 
            label_column='label'
        )
        
        model = self.baseline.train_model(X_train, y_train)
        metrics = self.baseline.evaluate_model(model, X_test, y_test)
        
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1' in metrics
        assert all(0 <= value <= 1 for value in metrics.values())
    
    def test_feature_importance(self):
        """Test feature importance extraction"""
        X_train, X_test, y_train, y_test = self.baseline.prepare_data(
            self.test_data, 
            text_column='text', 
            label_column='label'
        )
        
        model = self.baseline.train_model(X_train, y_train)
        feature_importance = self.baseline.get_feature_importance(model)
        
        assert isinstance(feature_importance, dict)
        assert len(feature_importance) > 0


class TestEvaluationReport:
    """Unit tests for EvaluationReport"""
    
    def setup_method(self):
        """Setup test data"""
        self.evaluator = EvaluationReport()
        self.y_true = [1, 0, 1, 0, 1, 0, 1, 0]
        self.y_pred = [1, 0, 1, 1, 1, 0, 0, 0]
        self.y_proba = [0.9, 0.1, 0.8, 0.6, 0.7, 0.2, 0.4, 0.3]
    
    def test_basic_metrics_calculation(self):
        """Test basic metrics calculation"""
        metrics = self.evaluator.calculate_metrics(self.y_true, self.y_pred)
        
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1' in metrics
        assert all(isinstance(value, float) for value in metrics.values())
    
    def test_confusion_matrix(self):
        """Test confusion matrix generation"""
        cm = self.evaluator.create_confusion_matrix(self.y_true, self.y_pred)
        
        assert cm.shape == (2, 2)
        assert cm.dtype == np.int64
        assert np.sum(cm) == len(self.y_true)
    
    def test_roc_curve(self):
        """Test ROC curve calculation"""
        fpr, tpr, thresholds = self.evaluator.calculate_roc_curve(
            self.y_true, self.y_proba
        )
        
        assert len(fpr) == len(tpr)
        assert len(tpr) == len(thresholds)
        assert all(0 <= value <= 1 for value in fpr)
        assert all(0 <= value <= 1 for value in tpr)
    
    def test_precision_recall_curve(self):
        """Test precision-recall curve calculation"""
        precision, recall, thresholds = self.evaluator.calculate_pr_curve(
            self.y_true, self.y_proba
        )
        
        assert len(precision) == len(recall)
        assert len(recall) == len(thresholds)
        assert all(0 <= value <= 1 for value in precision)
        assert all(0 <= value <= 1 for value in recall)
    
    def test_classification_report(self):
        """Test classification report generation"""
        report = self.evaluator.generate_classification_report(
            self.y_true, self.y_pred
        )
        
        assert isinstance(report, str)
        assert 'precision' in report.lower()
        assert 'recall' in report.lower()
        assert 'f1-score' in report.lower()
    
    def test_model_comparison(self):
        """Test model comparison functionality"""
        models_results = {
            'model1': {'y_true': self.y_true, 'y_pred': self.y_pred},
            'model2': {'y_true': self.y_true, 'y_pred': [1, 1, 1, 0, 1, 0, 1, 0]}
        }
        
        comparison = self.evaluator.compare_models(models_results)
        
        assert isinstance(comparison, pd.DataFrame)
        assert 'model1' in comparison.columns
        assert 'model2' in comparison.columns
        assert 'accuracy' in comparison.index
    
    def test_generate_report(self):
        """Test comprehensive report generation"""
        report = self.evaluator.generate_report(
            self.y_true, 
            self.y_pred, 
            self.y_proba,
            model_name='TestModel'
        )
        
        assert 'metrics' in report
        assert 'confusion_matrix' in report
        assert 'roc_curve' in report
        assert 'pr_curve' in report
        assert 'classification_report' in report


class TestMLflowUtils:
    """Unit tests for MLflowUtils"""
    
    def setup_method(self):
        """Setup test data"""
        self.mlflow_utils = MLflowUtils()
        self.test_metrics = {
            'accuracy': 0.85,
            'precision': 0.82,
            'recall': 0.88,
            'f1': 0.85
        }
        self.test_params = {
            'learning_rate': 0.001,
            'batch_size': 32,
            'epochs': 10
        }
    
    @patch('src.ml.mlflow_utils.mlflow')
    def test_log_experiment(self, mock_mlflow):
        """Test experiment logging"""
        mock_mlflow.start_run.return_value.__enter__ = lambda x: None
        mock_mlflow.start_run.return_value.__exit__ = lambda x, y, z, w: None
        
        self.mlflow_utils.log_experiment(
            experiment_name='test_experiment',
            metrics=self.test_metrics,
            parameters=self.test_params,
            model=Mock()
        )
        
        mock_mlflow.set_experiment.assert_called_once_with('test_experiment')
        mock_mlflow.start_run.assert_called_once()
        mock_mlflow.log_metrics.assert_called_once_with(self.test_metrics)
        mock_mlflow.log_params.assert_called_once_with(self.test_params)
    
    @patch('src.ml.mlflow_utils.mlflow')
    def test_load_model(self, mock_mlflow):
        """Test model loading"""
        mock_model = Mock()
        mock_mlflow.pyfunc.load_model.return_value = mock_model
        
        loaded_model = self.mlflow_utils.load_model('model_uri')
        
        assert loaded_model == mock_model
        mock_mlflow.pyfunc.load_model.assert_called_once_with('model_uri')
    
    @patch('src.ml.mlflow_utils.mlflow')
    def test_search_experiments(self, mock_mlflow):
        """Test experiment search"""
        mock_experiments = [Mock(), Mock()]
        mock_mlflow.search_experiments.return_value = mock_experiments
        
        experiments = self.mlflow_utils.search_experiments('test')
        
        assert experiments == mock_experiments
        mock_mlflow.search_experiments.assert_called_once()
    
    @patch('src.ml.mlflow_utils.mlflow')
    def test_get_best_run(self, mock_mlflow):
        """Test getting best run"""
        mock_run = Mock()
        mock_run.data.metrics = {'accuracy': 0.9}
        mock_mlflow.search_runs.return_value = [mock_run]
        
        best_run = self.mlflow_utils.get_best_run('experiment_id', 'accuracy')
        
        assert best_run == mock_run
        mock_mlflow.search_runs.assert_called_once()
    
    def test_validate_metrics(self):
        """Test metrics validation"""
        # Valid metrics
        assert self.mlflow_utils.validate_metrics(self.test_metrics) == True
        
        # Invalid metrics (non-numeric)
        invalid_metrics = {'accuracy': 'invalid', 'precision': 0.82}
        assert self.mlflow_utils.validate_metrics(invalid_metrics) == False
    
    def test_validate_parameters(self):
        """Test parameters validation"""
        # Valid parameters
        assert self.mlflow_utils.validate_parameters(self.test_params) == True
        
        # Invalid parameters (None values)
        invalid_params = {'learning_rate': None, 'batch_size': 32}
        assert self.mlflow_utils.validate_parameters(invalid_params) == False


