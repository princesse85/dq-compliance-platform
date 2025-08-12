import os
import logging
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from typing import Optional

logger = logging.getLogger(__name__)

class TransformerModel:
    """Transformer model using DistilBERT or LegalBERT."""
    
    def __init__(self, model_path: str = None):
        """Initialize the transformer model.
        
        Args:
            model_path: Path to the saved model. If None, uses default location.
        """
        if model_path is None:
            model_path = os.path.join(os.getcwd(), "models", "transformer")
        
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.classes_ = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained transformer model from disk."""
        try:
            logger.info(f"Loading transformer model from {self.model_path}")
            
            # Check if model files exist
            if not os.path.exists(self.model_path):
                logger.warning(f"Model path {self.model_path} does not exist, creating dummy model")
                self._create_dummy_model()
                return
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            
            # Create pipeline for easy inference
            self.pipeline = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1 if not torch.cuda.is_available() else 0,  # Use CPU if no GPU
                return_all_scores=True
            )
            
            # Extract class labels from model config
            if hasattr(self.model.config, 'label2id'):
                # Reverse the mapping to get id2label
                id2label = {v: k for k, v in self.model.config.label2id.items()}
                self.classes_ = [id2label[i] for i in range(len(id2label))]
            else:
                # Default classes
                self.classes_ = ['LowRisk', 'HighRisk']
            
            logger.info(f"Transformer model loaded successfully. Classes: {self.classes_}")
            
        except Exception as e:
            logger.error(f"Failed to load transformer model: {str(e)}")
            self._create_dummy_model()
    
    def _create_dummy_model(self):
        """Create a dummy transformer model for testing."""
        logger.warning("Creating dummy transformer model for testing")
        
        try:
            # Try to load a small pre-trained model
            model_name = "distilbert-base-uncased"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name, 
                num_labels=2,
                id2label={0: "LowRisk", 1: "HighRisk"},
                label2id={"LowRisk": 0, "HighRisk": 1}
            )
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1,  # Use CPU
                return_all_scores=True
            )
            
            self.classes_ = ['LowRisk', 'HighRisk']
            logger.info("Dummy transformer model created using DistilBERT")
            
        except Exception as e:
            logger.error(f"Failed to create dummy transformer model: {str(e)}")
            # Create a simple fallback
            self.classes_ = ['LowRisk', 'HighRisk']
    
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
            # Truncate text if too long (transformer models have token limits)
            max_length = 512
            if len(text) > max_length * 4:  # Rough estimate: 4 chars per token
                text = text[:max_length * 4]
            
            result = self.pipeline(text)
            
            # Get the prediction with highest score
            scores = result[0]
            best_score = max(scores, key=lambda x: x['score'])
            prediction = best_score['label']
            
            return prediction
            
        except Exception as e:
            logger.error(f"Transformer prediction failed: {str(e)}")
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
            # Truncate text if too long
            max_length = 512
            if len(text) > max_length * 4:
                text = text[:max_length * 4]
            
            result = self.pipeline(text)
            scores = result[0]
            
            # Find HighRisk probability
            for score in scores:
                if score['label'] == 'HighRisk':
                    return float(score['score'])
            
            # If HighRisk not found, return probability of last class
            return float(scores[-1]['score'])
            
        except Exception as e:
            logger.error(f"Transformer probability prediction failed: {str(e)}")
            return 0.5  # Default to 50% on error
    
    def get_token_importance(self, text: str, top_k: int = 10) -> list:
        """Get token importance scores for explanation.
        
        Args:
            text: Input text
            top_k: Number of top tokens to return
            
        Returns:
            List of (token, importance_score) tuples
        """
        if self.tokenizer is None or self.model is None:
            return []
        
        try:
            # Tokenize the text
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512,
                padding=True
            )
            
            # Get model outputs
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                
                # Get attention weights (simplified approach)
                # For a more sophisticated approach, you'd use integrated gradients or LIME
                attention_weights = outputs.attentions[-1] if outputs.attentions else None
                
                if attention_weights is not None:
                    # Average attention weights across heads
                    avg_attention = attention_weights.mean(dim=1).squeeze()
                    
                    # Get tokens
                    tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
                    
                    # Create token-importance pairs
                    token_importance = []
                    for i, (token, importance) in enumerate(zip(tokens, avg_attention)):
                        if token not in ['[CLS]', '[SEP]', '[PAD]']:
                            token_importance.append((token, float(importance)))
                    
                    # Sort by importance and return top_k
                    token_importance.sort(key=lambda x: x[1], reverse=True)
                    return token_importance[:top_k]
                else:
                    # Fallback: return first few tokens
                    tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
                    return [(token, 1.0) for token in tokens[:top_k] if token not in ['[CLS]', '[SEP]', '[PAD]']]
                    
        except Exception as e:
            logger.error(f"Failed to get token importance: {str(e)}")
            return []
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        return {
            "model_type": "transformer",
            "classes": self.classes_,
            "model_path": self.model_path,
            "tokenizer_loaded": self.tokenizer is not None,
            "model_loaded": self.model is not None,
            "pipeline_loaded": self.pipeline is not None
        }
