import os
import json
import pathlib
import logging
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.preprocessing import LabelEncoder
import pickle
import torch

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
MODEL_DIR = pathlib.Path("analytics/models/transformer/final_model")
CONFIG_FILE = MODEL_DIR / "config.json"
LABEL_ENCODER_FILE = pathlib.Path("analytics/models/transformer/label_encoder.pkl")

def load_model_and_tokenizer():
    """Load the trained transformer model and tokenizer."""
    try:
        # Load model configuration
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
        
        # Load model
        model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
        
        # Load label encoder (create if doesn't exist)
        if LABEL_ENCODER_FILE.exists():
            with open(LABEL_ENCODER_FILE, 'rb') as f:
                label_encoder = pickle.load(f)
        else:
            # Create label encoder with the classes we know
            label_encoder = LabelEncoder()
            label_encoder.fit(['HighRisk', 'LowRisk', 'MediumRisk'])
            # Save it for future use
            with open(LABEL_ENCODER_FILE, 'wb') as f:
                pickle.dump(label_encoder, f)
        
        logger.info("Model, tokenizer, and label encoder loaded successfully")
        return model, tokenizer, label_encoder, config
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None, None, None, None

def predict_risk(text, model, tokenizer, label_encoder, max_length=128):
    """Predict risk level for given text."""
    try:
        # Tokenize input
        inputs = tokenizer(
            text, 
            truncation=True, 
            padding="max_length", 
            max_length=max_length, 
            return_tensors="pt"
        )
        
        # Get prediction
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_class = torch.argmax(predictions, dim=1).item()
            confidence = predictions[0][predicted_class].item()
        
        # Decode label
        risk_level = label_encoder.inverse_transform([predicted_class])[0]
        
        return {
            'risk_level': risk_level,
            'confidence': confidence,
            'probabilities': predictions[0].numpy().tolist()
        }
        
    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        return None

def test_model():
    """Test the trained model with sample texts."""
    model, tokenizer, label_encoder, config = load_model_and_tokenizer()
    
    if model is None:
        logger.error("Failed to load model")
        return
    
    # Test samples
    test_texts = [
        "This is a high-risk transaction with suspicious patterns",
        "Normal business activity with standard compliance",
        "Medium risk operation requiring additional review"
    ]
    
    logger.info("Testing model with sample texts...")
    
    for text in test_texts:
        result = predict_risk(text, model, tokenizer, label_encoder)
        if result:
            logger.info(f"Text: {text[:50]}...")
            logger.info(f"Risk Level: {result['risk_level']}")
            logger.info(f"Confidence: {result['confidence']:.3f}")
            logger.info("---")

if __name__ == "__main__":
    logger.info("Starting model integration...")
    test_model()
    logger.info("Model integration completed!")
