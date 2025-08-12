import json
import time
import logging
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel, Field

from .load_baseline import BaselineModel
from .load_transformer import TransformerModel
from .explain_baseline import BaselineExplainer
from .explain_transformer import TransformerExplainer
from .utils import get_s3_presigned_url

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ML Inference API",
    description="Simple ML inference API with A/B testing",
    version="1.0.0",
)

# Global model instances (lazy loaded)
baseline_model = None
transformer_model = None
baseline_explainer = None
transformer_explainer = None

# Request/Response models
class PredictionRequest(BaseModel):
    text: Optional[str] = Field(None, description="Text to classify")
    doc_id: Optional[str] = Field(None, description="Optional document ID for pre-computed explanations")
    model: str = Field("auto", description="Model to use")
    explain: bool = Field(True, description="Whether to include explanation")

class PredictionResponse(BaseModel):
    model: str = Field(..., description="Model used for prediction")
    label: str = Field(..., description="Predicted label")
    confidence: float = Field(..., description="Prediction confidence")
    explanation: Dict[str, Any] = Field(..., description="Explanation details")
    timings_ms: Dict[str, int] = Field(..., description="Request timing breakdown")

def get_model_variant() -> str:
    """Get the model variant from environment variable."""
    return os.getenv("MODEL_VARIANT", "baseline")

def load_models():
    """Lazy load models based on the variant."""
    global baseline_model, transformer_model, baseline_explainer, transformer_explainer
    
    model_variant = get_model_variant()
    
    if model_variant == "baseline" and baseline_model is None:
        logger.info("Loading baseline model...")
        try:
            baseline_model = BaselineModel()
            baseline_explainer = BaselineExplainer(baseline_model)
            logger.info("Baseline model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load baseline model: {str(e)}")
            raise HTTPException(status_code=500, detail="Model loading failed")
        
    elif model_variant == "transformer" and transformer_model is None:
        logger.info("Loading transformer model...")
        try:
            transformer_model = TransformerModel()
            transformer_explainer = TransformerExplainer(transformer_model)
            logger.info("Transformer model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load transformer model: {str(e)}")
            raise HTTPException(status_code=500, detail="Model loading failed")

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest) -> PredictionResponse:
    """Main prediction endpoint with A/B testing support."""
    start_time = time.time()
    
    try:
        # Validate request
        if not request.text and not request.doc_id:
            raise HTTPException(status_code=400, detail="Either 'text' or 'doc_id' must be provided")
        
        # Load models based on variant
        load_models()
        
        # Determine which model to use
        model_variant = get_model_variant()
        if request.model == "auto":
            # Use the variant specified in environment
            pass
        elif request.model in ["baseline", "transformer"]:
            model_variant = request.model
        else:
            raise HTTPException(status_code=400, detail="Invalid model specified")
        
        # Perform prediction
        pre_time = time.time()
        
        if model_variant == "baseline":
            if not baseline_model:
                raise HTTPException(status_code=500, detail="Baseline model not loaded")
            
            # Get prediction
            prediction = baseline_model.predict(request.text or "")
            confidence = baseline_model.predict_proba(request.text or "")
            
            # Get explanation if requested
            explanation = {}
            if request.explain:
                explanation = baseline_explainer.explain(request.text or "")
            
        elif model_variant == "transformer":
            if not transformer_model:
                raise HTTPException(status_code=500, detail="Transformer model not loaded")
            
            # Get prediction
            prediction = transformer_model.predict(request.text or "")
            confidence = transformer_model.predict_proba(request.text or "")
            
            # Get explanation if requested
            explanation = {}
            if request.explain:
                explanation = transformer_explainer.explain(
                    text=request.text or "",
                    doc_id=request.doc_id
                )
        
        else:
            raise HTTPException(status_code=500, detail="Unknown model variant")
        
        infer_time = time.time()
        
        # Calculate timings
        timings = {
            "pre": int((pre_time - start_time) * 1000),
            "infer": int((infer_time - pre_time) * 1000),
            "post": int((time.time() - infer_time) * 1000)
        }
        
        # Log successful prediction
        logger.info(f"Prediction successful - Model: {model_variant}, Label: {prediction}, Confidence: {confidence:.3f}")
        
        return PredictionResponse(
            model=model_variant,
            label=prediction,
            confidence=confidence,
            explanation=explanation,
            timings_ms=timings
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_variant": get_model_variant(),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }

@app.get("/models")
async def list_models():
    """List available models and their status."""
    return {
        "available_models": ["baseline", "transformer"],
        "current_variant": get_model_variant(),
        "baseline_loaded": baseline_model is not None,
        "transformer_loaded": transformer_model is not None
    }

# Lambda handler for AWS Lambda
def handler(event, context):
    """AWS Lambda handler using Mangum adapter."""
    asgi_handler = Mangum(app, lifespan="off")
    return asgi_handler(event, context)
