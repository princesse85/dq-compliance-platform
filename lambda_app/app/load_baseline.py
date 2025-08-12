import os
import joblib
import logging
from typing import List, Tuple
import numpy as np
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

class BaselineModel:
    """Baseline model using TF-IDF + Logistic Regression."""
    
    def __init__(self, model_path: str = None):
        """Initialize the baseline model.
        
        Args:
            model_path: Path to the saved model. If None, uses default location.
        """
        if model_path is None:
            model_path = os.path.join(os.getcwd(), "models", "baseline", "model.joblib")
        
        self.model_path = model_path
        self.pipeline = None
        self.classes_ = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained model from disk."""
        try:
            logger.info(f"Loading baseline model from {self.model_path}")
            self.pipeline = joblib.load(self.model_path)
            
            # Extract classes from the pipeline
            if hasattr(self.pipeline, 'named_steps'):
                # Get the classifier from the pipeline
                classifier = self.pipeline.named_steps.get('classifier', None)
                if classifier is None:
                    # Try to find the classifier step
                    for step_name, step in self.pipeline.named_steps.items():
                        if hasattr(step, 'classes_'):
                            classifier = step
                            break
                
                if classifier and hasattr(classifier, 'classes_'):
                    self.classes_ = classifier.classes_
                else:
                    # Default classes for binary classification
                    self.classes_ = np.array(['LowRisk', 'HighRisk'])
            else:
                # Fallback classes
                self.classes_ = np.array(['LowRisk', 'HighRisk'])
                
            logger.info(f"Baseline model loaded successfully. Classes: {self.classes_}")
            
        except Exception as e:
            logger.error(f"Failed to load baseline model: {str(e)}")
            # Create a dummy model for testing
            self._create_dummy_model()
    
    def _create_dummy_model(self):
        """Create a dummy model for testing when the real model is not available."""
        logger.warning("Creating dummy baseline model for testing")
        
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        
        # Create a simple dummy pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
            ('classifier', LogisticRegression(random_state=42))
        ])
        
        # Train on dummy data
        dummy_texts = [
            "This is a low risk contract with standard terms.",
            "This is a high risk contract with indemnification clauses.",
            "Standard service agreement with normal liability limits.",
            "Contract includes unlimited liability and indemnification."
        ]
        dummy_labels = ['LowRisk', 'HighRisk', 'LowRisk', 'HighRisk']
        
        self.pipeline.fit(dummy_texts, dummy_labels)
        self.classes_ = np.array(['LowRisk', 'HighRisk'])
        
        logger.info("Dummy baseline model created and trained")
    
    def predict(self, text: str) -> str:
        """Predict the risk level for the given text.
        
        Args:
            text: Input text to classify
            
        Returns:
            Predicted label ('LowRisk' or 'HighRisk')
        """
        if self.pipeline is None:
            raise ValueError("Model not loaded")
        
        try:
            prediction = self.pipeline.predict([text])[0]
            return str(prediction)
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return "LowRisk"  # Default to low risk on error
    
    def predict_proba(self, text: str) -> float:
        """Get prediction probability for the positive class (HighRisk).
        
        Args:
            text: Input text to classify
            
        Returns:
            Probability of HighRisk class
        """
        if self.pipeline is None:
            raise ValueError("Model not loaded")
        
        try:
            proba = self.pipeline.predict_proba([text])[0]
            
            # Find the index of HighRisk class
            high_risk_idx = np.where(self.classes_ == 'HighRisk')[0]
            if len(high_risk_idx) > 0:
                return float(proba[high_risk_idx[0]])
            else:
                # If HighRisk not in classes, return probability of last class
                return float(proba[-1])
                
        except Exception as e:
            logger.error(f"Probability prediction failed: {str(e)}")
            return 0.5  # Default to 50% on error
    
    def get_feature_names(self) -> List[str]:
        """Get feature names from the TF-IDF vectorizer.
        
        Returns:
            List of feature names (words/phrases)
        """
        if self.pipeline is None:
            return []
        
        try:
            tfidf_step = self.pipeline.named_steps.get('tfidf', None)
            if tfidf_step and hasattr(tfidf_step, 'get_feature_names_out'):
                return tfidf_step.get_feature_names_out().tolist()
            elif tfidf_step and hasattr(tfidf_step, 'get_feature_names'):
                return tfidf_step.get_feature_names().tolist()
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to get feature names: {str(e)}")
            return []
    
    def get_coefficients(self) -> List[Tuple[str, float]]:
        """Get feature coefficients from the logistic regression model.
        
        Returns:
            List of (feature_name, coefficient) tuples
        """
        if self.pipeline is None:
            return []
        
        try:
            classifier = self.pipeline.named_steps.get('classifier', None)
            if classifier is None:
                # Try to find the classifier step
                for step_name, step in self.pipeline.named_steps.items():
                    if hasattr(step, 'coef_'):
                        classifier = step
                        break
            
            if classifier and hasattr(classifier, 'coef_'):
                feature_names = self.get_feature_names()
                coefficients = classifier.coef_[0]  # Get coefficients for first class
                
                # Create list of (feature_name, coefficient) tuples
                feature_coeffs = list(zip(feature_names, coefficients))
                
                # Sort by absolute coefficient value (most important first)
                feature_coeffs.sort(key=lambda x: abs(x[1]), reverse=True)
                
                return feature_coeffs
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get coefficients: {str(e)}")
            return []
