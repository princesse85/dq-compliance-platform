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
    Load ML model from S3 or cache with performance optimization.
    
    Args:
        model_name: Name of the model to load
        
    Returns:
        Loaded model object
    """
    if model_name is None:
        model_name = MODEL_VARIANT
    
    # Check cache first for performance optimization
    if model_name in _model_cache:
        log.info(f"Using cached model: {model_name}")
        return _model_cache[model_name]
    
    try:
        # Performance optimization: Load model asynchronously in production
        log.info(f"Loading model: {model_name}")
        
        # Production-ready model loading with error handling and metrics
        start_time = datetime.utcnow()
        
        # Mock model for demonstration - in production this would load from S3
        mock_model = {
            'name': model_name,
            'version': '1.0.0',
            'loaded_at': start_time.isoformat(),
            'type': 'text_classifier',
            'model_size_mb': 50,  # Track model size for monitoring
            'load_time_ms': 250,  # Track load time for performance
            'memory_usage_mb': 128  # Track memory usage
        }
        
        # Cache model for performance (with TTL in production)
        _model_cache[model_name] = mock_model
        
        # Log performance metrics
        load_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        log.info(f"Model {model_name} loaded successfully in {load_time:.2f}ms")
        
        return mock_model
        
    except Exception as e:
        log.error(f"Failed to load model {model_name}: {str(e)}")
        raise

def predict(text: str, model_name: str = None) -> Dict[str, Any]:
    """
    Make prediction using the specified model with performance optimization.
    
    Args:
        text: Input text for prediction
        model_name: Name of the model to use
        
    Returns:
        Prediction results with timing metrics
    """
    start_time = datetime.utcnow()
    
    try:
        # Performance tracking
        model_load_start = datetime.utcnow()
        model = load_model(model_name)
        model_load_time = (datetime.utcnow() - model_load_start).total_seconds() * 1000
        
        # Input validation and preprocessing
        if not text or len(text.strip()) == 0:
            raise ValueError("Input text cannot be empty")
        
        # Limit text length for performance
        if len(text) > 10000:
            text = text[:10000]
            log.warning("Input text truncated to 10000 characters for performance")
        
        # Mock prediction logic with performance simulation
        prediction_start = datetime.utcnow()
        
        # Simulate different model performance characteristics
        if model_name == 'baseline':
            prediction_time = 50  # ms
            confidence = 0.82
        elif model_name == 'transformer':
            prediction_time = 200  # ms
            confidence = 0.92
        else:
            prediction_time = 100  # ms
            confidence = 0.87
        
        # Improved prediction logic based on text analysis
        compliance_indicators = ['compliant', 'standard', 'agreement', 'terms', 'conditions']
        risk_indicators = ['indemnify', 'liability', 'damages', 'breach', 'penalty']
        
        text_lower = text.lower()
        compliance_score = sum(1 for indicator in compliance_indicators if indicator in text_lower)
        risk_score = sum(1 for indicator in risk_indicators if indicator in text_lower)
        
        # Determine label based on analysis
        if risk_score > compliance_score:
            label = 'HIGH_RISK'
            risk_value = 0.8
        elif len(text) > 200 and compliance_score > 0:
            label = 'COMPLIANT'
            risk_value = 0.2
        else:
            label = 'MEDIUM_RISK'
            risk_value = 0.5
        
        prediction_time_actual = (datetime.utcnow() - prediction_start).total_seconds() * 1000
        total_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        prediction = {
            'model_name': model['name'],
            'model_version': model['version'],
            'input_text': text[:500] + '...' if len(text) > 500 else text,
            'input_length': len(text),
            'prediction': {
                'label': label,
                'confidence': confidence,
                'risk_score': risk_value
            },
            'performance_metrics': {
                'model_load_time_ms': model_load_time,
                'prediction_time_ms': prediction_time_actual,
                'total_time_ms': total_time,
                'memory_usage_mb': model.get('memory_usage_mb', 128)
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        log.info(f"Prediction completed in {total_time:.2f}ms for {len(text)} characters")
        return prediction
        
    except Exception as e:
        total_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        log.error(f"Prediction failed after {total_time:.2f}ms: {str(e)}")
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
