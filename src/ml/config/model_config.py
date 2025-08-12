"""
Model Configuration for Enhanced Phase 3 Pipeline
================================================

This module contains all configuration parameters for the enhanced ML pipeline,
including model hyperparameters, training settings, and experiment configurations.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class DataConfig:
    """Configuration for data processing and generation."""
    
    # Data paths
    data_dir: str = "data/text_corpus"
    output_dir: str = "analytics/models"
    
    # Dataset parameters
    train_size: int = 840
    valid_size: int = 180
    test_size: int = 180
    total_samples: int = 1200
    
    # Text processing
    max_text_length: int = 512
    min_text_length: int = 50
    
    # Class distribution
    num_classes: int = 3
    class_names: List[str] = None
    
    def __post_init__(self):
        if self.class_names is None:
            self.class_names = ['HighRisk', 'MediumRisk', 'LowRisk']

@dataclass
class BaselineModelConfig:
    """Configuration for baseline models."""
    
    # Model types
    models: List[str] = None
    
    # TF-IDF parameters
    tfidf_max_features: List[int] = None
    tfidf_ngram_ranges: List[tuple] = None
    tfidf_min_df: List[int] = None
    tfidf_max_df: List[float] = None
    
    # Hyperparameter optimization
    n_trials: int = 30
    cv_folds: int = 5
    
    # Model-specific parameters
    logistic_regression_params: Dict[str, Any] = None
    random_forest_params: Dict[str, Any] = None
    xgboost_params: Dict[str, Any] = None
    lightgbm_params: Dict[str, Any] = None
    svm_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.models is None:
            self.models = ['logistic_regression', 'random_forest', 'xgboost', 'lightgbm', 'svm']
        
        if self.tfidf_max_features is None:
            self.tfidf_max_features = [5000, 10000, 15000]
        
        if self.tfidf_ngram_ranges is None:
            self.tfidf_ngram_ranges = [(1, 1), (1, 2), (1, 3)]
        
        if self.tfidf_min_df is None:
            self.tfidf_min_df = [1, 2, 5]
        
        if self.tfidf_max_df is None:
            self.tfidf_max_df = [0.8, 0.9, 0.95]
        
        if self.logistic_regression_params is None:
            self.logistic_regression_params = {
                'C': [0.1, 1.0, 10.0, 100.0],
                'class_weight': [None, 'balanced']
            }
        
        if self.random_forest_params is None:
            self.random_forest_params = {
                'n_estimators': [100, 200, 300],
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5, 10],
                'class_weight': [None, 'balanced', 'balanced_subsample']
            }
        
        if self.xgboost_params is None:
            self.xgboost_params = {
                'n_estimators': [100, 200],
                'max_depth': [3, 6, 9],
                'learning_rate': [0.01, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0]
            }
        
        if self.lightgbm_params is None:
            self.lightgbm_params = {
                'n_estimators': [100, 200],
                'max_depth': [3, 6, 9],
                'learning_rate': [0.01, 0.1, 0.2],
                'num_leaves': [31, 62, 127]
            }
        
        if self.svm_params is None:
            self.svm_params = {
                'C': [0.1, 1.0, 10.0],
                'class_weight': [None, 'balanced']
            }

@dataclass
class TransformerModelConfig:
    """Configuration for transformer models."""
    
    # Model architectures
    models: Dict[str, Dict[str, Any]] = None
    
    # Training parameters
    max_length: int = 256
    batch_sizes: List[int] = None
    learning_rates: List[float] = None
    epochs: List[int] = None
    weight_decay: List[float] = None
    warmup_steps: List[int] = None
    
    # Optimization
    n_trials: int = 15
    cv_folds: int = 3
    
    # Early stopping
    early_stopping_patience: int = 2
    
    def __post_init__(self):
        if self.models is None:
            self.models = {
                'distilbert': {
                    'name': 'distilbert-base-uncased',
                    'max_length': 256,
                    'batch_size': 16,
                    'learning_rate': 2e-5,
                    'epochs': 3,
                    'weight_decay': 0.01,
                    'warmup_steps': 100
                },
                'bert': {
                    'name': 'bert-base-uncased',
                    'max_length': 256,
                    'batch_size': 8,
                    'learning_rate': 2e-5,
                    'epochs': 3,
                    'weight_decay': 0.01,
                    'warmup_steps': 100
                },
                'roberta': {
                    'name': 'roberta-base',
                    'max_length': 256,
                    'batch_size': 16,
                    'learning_rate': 2e-5,
                    'epochs': 3,
                    'weight_decay': 0.01,
                    'warmup_steps': 100
                },
                'legal_bert': {
                    'name': 'nlpaueb/legal-bert-base-uncased',
                    'max_length': 256,
                    'batch_size': 8,
                    'learning_rate': 2e-5,
                    'epochs': 3,
                    'weight_decay': 0.01,
                    'warmup_steps': 100
                },
                'deberta': {
                    'name': 'microsoft/deberta-base',
                    'max_length': 256,
                    'batch_size': 8,
                    'learning_rate': 2e-5,
                    'epochs': 3,
                    'weight_decay': 0.01,
                    'warmup_steps': 100
                }
            }
        
        if self.batch_sizes is None:
            self.batch_sizes = [4, 8, 16]
        
        if self.learning_rates is None:
            self.learning_rates = [1e-5, 2e-5, 3e-5, 5e-5]
        
        if self.epochs is None:
            self.epochs = [2, 3, 5]
        
        if self.weight_decay is None:
            self.weight_decay = [0.01, 0.05, 0.1]
        
        if self.warmup_steps is None:
            self.warmup_steps = [50, 100, 150, 200]

@dataclass
class ExplainabilityConfig:
    """Configuration for explainability analysis."""
    
    # LIME parameters
    lime_n_samples_per_class: int = 5
    lime_num_features: int = 15
    lime_num_samples: int = 1000
    
    # Feature importance
    top_features_count: int = 20
    wordcloud_max_words: int = 100
    
    # Visualization
    plot_figsize: tuple = (12, 8)
    dpi: int = 300
    
    # Output formats
    save_html: bool = True
    save_json: bool = True
    save_plots: bool = True

@dataclass
class MLflowConfig:
    """Configuration for MLflow tracking."""
    
    # Experiment settings
    experiment_name: str = "enhanced_phase3_pipeline"
    tracking_uri: str = "sqlite:///mlflow.db"
    
    # Logging
    log_artifacts: bool = True
    log_models: bool = True
    log_parameters: bool = True
    log_metrics: bool = True
    
    # Artifact storage
    artifact_location: str = "mlruns"

@dataclass
class PipelineConfig:
    """Main pipeline configuration."""
    
    # Pipeline components
    enable_data_generation: bool = True
    enable_baseline_models: bool = True
    enable_transformer_models: bool = True
    enable_explainability: bool = True
    
    # Execution settings
    random_seed: int = 42
    num_workers: int = 4
    device: str = "auto"  # "cpu", "cuda", or "auto"
    
    # Data configurations
    data: DataConfig = None
    baseline: BaselineModelConfig = None
    transformer: TransformerModelConfig = None
    explainability: ExplainabilityConfig = None
    mlflow: MLflowConfig = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = DataConfig()
        if self.baseline is None:
            self.baseline = BaselineModelConfig()
        if self.transformer is None:
            self.transformer = TransformerModelConfig()
        if self.explainability is None:
            self.explainability = ExplainabilityConfig()
        if self.mlflow is None:
            self.mlflow = MLflowConfig()

# Default configuration instance
DEFAULT_CONFIG = PipelineConfig()

def get_config() -> PipelineConfig:
    """Get the default configuration."""
    return DEFAULT_CONFIG

def update_config(config: PipelineConfig, **kwargs) -> PipelineConfig:
    """Update configuration with new parameters."""
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config
