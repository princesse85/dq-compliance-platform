"""
ML Inference Lambda Handler for Enterprise Data Quality & Compliance Platform.

This module provides the main handler for the ML inference API, including
model loading, prediction endpoints, and health checks.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
import boto3
from datetime import datetime

# Configure logging
log = logging.getLogger()
log.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
ssm_client = boto3.client('ssm')

# Environment variables
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
PROJECT_PREFIX = os.environ.get('PROJECT_PREFIX', 'enterprise')
ANALYTICS_BUCKET = os.environ.get('ANALYTICS_BUCKET')
EXPLAIN_PREFIX = os.environ.get('EXPLAIN_PREFIX', 'explanations')
MODEL_VARIANT = os.environ.get('MODEL_VARIANT', 'baseline')

# Global model cache
_model_cache = {}

def load_model(model_name: str = None) -> Any:
    """
    Load ML model from S3 or cache.
    
    Args:
        model_name: Name of the model to load
        
    Returns:
        Loaded model object
    """
    if model_name is None:
        model_name = MODEL_VARIANT
    
    # Check cache first
    if model_name in _model_cache:
        log.info(f"Using cached model: {model_name}")
        return _model_cache[model_name]
    
    try:
        # In a real implementation, you would load the model from S3
        # For now, we'll return a mock model
        log.info(f"Loading model: {model_name}")
        
        # Mock model for demonstration
        mock_model = {
            'name': model_name,
            'version': '1.0.0',
            'loaded_at': datetime.utcnow().isoformat(),
            'type': 'text_classifier'
        }
        
        _model_cache[model_name] = mock_model
        return mock_model
        
    except Exception as e:
        log.error(f"Failed to load model {model_name}: {str(e)}")
        raise

def predict(text: str, model_name: str = None) -> Dict[str, Any]:
    """
    Make prediction using the specified model.
    
    Args:
        text: Input text for prediction
        model_name: Name of the model to use
        
    Returns:
        Prediction results
    """
    try:
        model = load_model(model_name)
        
        # Mock prediction logic
        # In a real implementation, you would use the actual model
        prediction = {
            'model_name': model['name'],
            'model_version': model['version'],
            'input_text': text,
            'prediction': {
                'label': 'COMPLIANT' if len(text) > 100 else 'NON_COMPLIANT',
                'confidence': 0.85,
                'risk_score': 0.15
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return prediction
        
    except Exception as e:
        log.error(f"Prediction failed: {str(e)}")
        raise

def get_health_status() -> Dict[str, Any]:
    """
    Get health status of the ML inference service.
    
    Returns:
        Health status information
    """
    try:
        # Check model availability
        model = load_model()
        
        # Check S3 connectivity
        s3_client.head_bucket(Bucket=ANALYTICS_BUCKET)
        
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': ENVIRONMENT,
            'model_loaded': True,
            'model_name': model['name'],
            's3_accessible': True
        }
        
    except Exception as e:
        log.error(f"Health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': ENVIRONMENT,
            'error': str(e)
        }

def get_models_status() -> Dict[str, Any]:
    """
    Get status of available models.
    
    Returns:
        Models status information
    """
    try:
        models = {}
        
        # Check available model variants
        for variant in ['baseline', 'advanced', 'production']:
            try:
                model = load_model(variant)
                models[variant] = {
                    'status': 'available',
                    'version': model['version'],
                    'loaded_at': model['loaded_at']
                }
            except Exception as e:
                models[variant] = {
                    'status': 'unavailable',
                    'error': str(e)
                }
        
        return {
            'models': models,
            'timestamp': datetime.utcnow().isoformat(),
            'environment': ENVIRONMENT
        }
        
    except Exception as e:
        log.error(f"Failed to get models status: {str(e)}")
        return {
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for ML inference API.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        # Parse request
        path = event.get('path', '')
        http_method = event.get('httpMethod', 'GET')
        body = event.get('body', '{}')
        
        # Parse body if it's a string
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                body = {}
        
        log.info(f"Request: {http_method} {path}")
        
        # Route requests
        if path == '/health' and http_method == 'GET':
            status = get_health_status()
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(status)
            }
        
        elif path == '/models' and http_method == 'GET':
            models_status = get_models_status()
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(models_status)
            }
        
        elif path == '/predict' and http_method == 'POST':
            # Validate input
            if 'text' not in body:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Missing required field: text'})
                }
            
            text = body['text']
            model_name = body.get('model', MODEL_VARIANT)
            
            # Make prediction
            prediction = predict(text, model_name)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(prediction)
            }
        
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Endpoint not found'})
            }
    
    except Exception as e:
        log.error(f"Handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
