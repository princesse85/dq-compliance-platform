"""
MLflow Tracking Utilities for Enhanced Phase 3 Pipeline
======================================================

This module provides enhanced MLflow tracking capabilities with proper error handling,
custom serialization, and production-ready features.
"""

import os
import json
import mlflow
import mlflow.sklearn
import mlflow.pytorch
from datetime import datetime
from typing import Dict, Any, Optional, List
import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import warnings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)
warnings.filterwarnings('ignore')

class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle numpy types."""
    
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

class MLflowTracker:
    """Enhanced MLflow tracking with comprehensive logging capabilities."""
    
    def __init__(self, 
                 experiment_name: str = "enhanced_phase3_pipeline",
                 tracking_uri: str = "sqlite:///mlflow.db",
                 artifact_location: str = "mlruns"):
        """
        Initialize MLflow tracker.
        
        Args:
            experiment_name: Name of the MLflow experiment
            tracking_uri: MLflow tracking URI
            artifact_location: Location for storing artifacts
        """
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri
        self.artifact_location = artifact_location
        self.run_id = None
        self.experiment_id = None
        
        # Initialize MLflow
        self._setup_mlflow()
    
    def _setup_mlflow(self):
        """Setup MLflow tracking."""
        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            
            # Get or create experiment
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                self.experiment_id = mlflow.create_experiment(
                    self.experiment_name,
                    artifact_location=self.artifact_location
                )
            else:
                self.experiment_id = experiment.experiment_id
                
        except Exception as e:
            logger.info(r"Warning: MLflow setup failed: {e}")
            logger.info(r"Continuing without MLflow tracking...")
    
    def start_run(self, run_name: str = None) -> bool:
        """
        Start a new MLflow run.
        
        Args:
            run_name: Name for the run
            
        Returns:
            bool: True if run started successfully, False otherwise
        """
        try:
            mlflow.start_run(
                experiment_id=self.experiment_id,
                run_name=run_name or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            self.run_id = mlflow.active_run().info.run_id
            return True
        except Exception as e:
            logger.info(r"Warning: Failed to start MLflow run: {e}")
            return False
    
    def end_run(self) -> bool:
        """
        End the current MLflow run.
        
        Returns:
            bool: True if run ended successfully, False otherwise
        """
        try:
            if mlflow.active_run():
                mlflow.end_run()
                return True
            return False
        except Exception as e:
            logger.info(r"Warning: Failed to end MLflow run: {e}")
            return False
    
    def log_parameters(self, params: Dict[str, Any]) -> bool:
        """
        Log parameters to MLflow.
        
        Args:
            params: Dictionary of parameters to log
            
        Returns:
            bool: True if parameters logged successfully, False otherwise
        """
        try:
            for key, value in params.items():
                if isinstance(value, (dict, list)):
                    mlflow.log_param(key, json.dumps(value, cls=NumpyEncoder))
                else:
                    mlflow.log_param(key, value)
            return True
        except Exception as e:
            logger.info(r"Warning: Failed to log parameters: {e}")
            return False
    
    def log_metrics(self, metrics: Dict[str, float]) -> bool:
        """
        Log metrics to MLflow.
        
        Args:
            metrics: Dictionary of metrics to log
            
        Returns:
            bool: True if metrics logged successfully, False otherwise
        """
        try:
            for key, value in metrics.items():
                mlflow.log_metric(key, float(value))
            return True
        except Exception as e:
            logger.info(r"Warning: Failed to log metrics: {e}")
            return False
    
    def log_artifacts(self, local_dir: str, artifact_path: str = None) -> bool:
        """
        Log artifacts to MLflow.
        
        Args:
            local_dir: Local directory containing artifacts
            artifact_path: Optional path within the artifact store
            
        Returns:
            bool: True if artifacts logged successfully, False otherwise
        """
        try:
            mlflow.log_artifacts(local_dir, artifact_path)
            return True
        except Exception as e:
            logger.info(r"Warning: Failed to log artifacts: {e}")
            return False
    
    def log_model(self, model, model_name: str, model_type: str = "sklearn") -> bool:
        """
        Log model to MLflow.
        
        Args:
            model: The model to log
            model_name: Name for the model
            model_type: Type of model ("sklearn" or "pytorch")
            
        Returns:
            bool: True if model logged successfully, False otherwise
        """
        try:
            if model_type == "sklearn":
                mlflow.sklearn.log_model(model, model_name)
            elif model_type == "pytorch":
                mlflow.pytorch.log_model(model, model_name)
            else:
                logger.info(r"Warning: Unknown model type: {model_type}")
                return False
            return True
        except Exception as e:
            logger.info(r"Warning: Failed to log model: {e}")
            return False
    
    def log_dataset_info(self, dataset_info: Dict[str, Any]) -> bool:
        """
        Log dataset information and statistics.
        
        Args:
            dataset_info: Dictionary containing dataset information
            
        Returns:
            bool: True if dataset info logged successfully, False otherwise
        """
        try:
            self.log_parameters({
                "dataset_size": dataset_info.get("size", 0),
                "num_classes": dataset_info.get("num_classes", 0),
                "class_distribution": json.dumps(
                    dataset_info.get("class_distribution", {}), 
                    cls=NumpyEncoder
                )
            })
            return True
        except Exception as e:
            logger.info(r"Warning: Failed to log dataset info: {e}")
            return False
    
    def log_confusion_matrix(self, cm: np.ndarray, class_names: List[str]) -> bool:
        """
        Log confusion matrix as a plot.
        
        Args:
            cm: Confusion matrix array
            class_names: List of class names
            
        Returns:
            bool: True if confusion matrix logged successfully, False otherwise
        """
        try:
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                       xticklabels=class_names, yticklabels=class_names)
            plt.title('Confusion Matrix')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
            plt.tight_layout()
            
            # Save to temporary file
            temp_path = "temp_confusion_matrix.png"
            plt.savefig(temp_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Log as artifact
            mlflow.log_artifact(temp_path, "confusion_matrix.png")
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return True
        except Exception as e:
            logger.info(r"Warning: Failed to log confusion matrix: {e}")
            return False
    
    def log_classification_report(self, report: Dict[str, Any]) -> bool:
        """
        Log classification report.
        
        Args:
            report: Classification report dictionary
            
        Returns:
            bool: True if classification report logged successfully, False otherwise
        """
        try:
            # Convert to JSON-serializable format
            serializable_report = {}
            for key, value in report.items():
                if isinstance(value, dict):
                    serializable_report[key] = {
                        k: float(v) if isinstance(v, (int, float, np.number)) else v
                        for k, v in value.items()
                    }
                else:
                    serializable_report[key] = value
            
            self.log_parameters({
                "classification_report": json.dumps(serializable_report, cls=NumpyEncoder)
            })
            return True
        except Exception as e:
            logger.info(r"Warning: Failed to log classification report: {e}")
            return False
    
    def log_experiment_summary(self, summary: Dict[str, Any]) -> bool:
        """
        Log experiment summary and conclusions.
        
        Args:
            summary: Dictionary containing experiment summary
            
        Returns:
            bool: True if summary logged successfully, False otherwise
        """
        try:
            self.log_parameters({
                "experiment_summary": json.dumps(summary, cls=NumpyEncoder)
            })
            return True
        except Exception as e:
            logger.info(r"Warning: Failed to log experiment summary: {e}")
            return False
    
    def log_model_parameters(self, model_params: Dict[str, Any]) -> bool:
        """
        Log model-specific parameters.
        
        Args:
            model_params: Dictionary of model parameters
            
        Returns:
            bool: True if model parameters logged successfully, False otherwise
        """
        try:
            for key, value in model_params.items():
                if isinstance(value, (dict, list)):
                    mlflow.log_param(key, json.dumps(value, cls=NumpyEncoder))
                else:
                    mlflow.log_param(key, value)
            return True
        except Exception as e:
            logger.info(r"Warning: Failed to log model parameters: {e}")
            return False
    
    def log_evaluation_metrics(self, metrics: Dict[str, float]) -> bool:
        """
        Log evaluation metrics.
        
        Args:
            metrics: Dictionary of evaluation metrics
            
        Returns:
            bool: True if evaluation metrics logged successfully, False otherwise
        """
        try:
            for key, value in metrics.items():
                mlflow.log_metric(f"eval_{key}", float(value))
            return True
        except Exception as e:
            logger.info(r"Warning: Failed to log evaluation metrics: {e}")
            return False

def create_mlflow_tracker(experiment_name: str = None, 
                         tracking_uri: str = None,
                         artifact_location: str = None) -> MLflowTracker:
    """
    Factory function to create MLflow tracker.
    
    Args:
        experiment_name: Name of the experiment
        tracking_uri: MLflow tracking URI
        artifact_location: Location for artifacts
        
    Returns:
        MLflowTracker: Configured MLflow tracker instance
    """
    return MLflowTracker(
        experiment_name=experiment_name or "enhanced_phase3_pipeline",
        tracking_uri=tracking_uri or "sqlite:///mlflow.db",
        artifact_location=artifact_location or "mlruns"
    )
