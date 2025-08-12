import os
import logging
import boto3
from typing import Dict, Any, Optional
from .load_transformer import TransformerModel
from .utils import get_s3_presigned_url

logger = logging.getLogger(__name__)

class TransformerExplainer:
    """Explainer for transformer models with pre-computed LIME/SHAP explanations."""
    
    def __init__(self, model: TransformerModel):
        """Initialize the explainer with a transformer model.
        
        Args:
            model: Loaded TransformerModel instance
        """
        self.model = model
        self.s3_client = boto3.client('s3')
        self.analytics_bucket = os.getenv('ANALYTICS_BUCKET', '')
        self.explain_prefix = os.getenv('EXPLAIN_PREFIX', 'explain')
    
    def explain(self, text: str, doc_id: Optional[str] = None, top_k: int = 10) -> Dict[str, Any]:
        """Generate explanation for the transformer model prediction.
        
        Args:
            text: Input text to explain
            doc_id: Optional document ID to look up pre-computed explanation
            top_k: Number of top tokens to return for saliency
            
        Returns:
            Dictionary containing explanation details
        """
        try:
            # Get prediction details
            prediction = self.model.predict(text)
            confidence = self.model.predict_proba(text)
            
            # Try to get pre-computed explanation if doc_id is provided
            html_url = None
            if doc_id:
                html_url = self._get_precomputed_explanation_url(doc_id)
            
            # Get token saliency for lightweight explanation
            token_saliency = self._get_token_saliency(text, top_k)
            
            # Determine prediction direction
            is_high_risk = prediction == "HighRisk"
            
            return {
                "type": "tokens",
                "top_terms": [token for token, _ in token_saliency],
                "token_saliency": {token: score for token, score in token_saliency},
                "prediction_direction": "high_risk" if is_high_risk else "low_risk",
                "confidence_level": self._get_confidence_level(confidence),
                "html_url": html_url,
                "explanation_method": "attention_saliency",
                "has_precomputed": html_url is not None,
                "doc_id": doc_id
            }
            
        except Exception as e:
            logger.error(f"Transformer explanation failed: {str(e)}")
            return self._fallback_explanation(text, doc_id)
    
    def _get_precomputed_explanation_url(self, doc_id: str) -> Optional[str]:
        """Get pre-signed URL for pre-computed LIME/SHAP explanation.
        
        Args:
            doc_id: Document ID to look up
            
        Returns:
            Pre-signed S3 URL if explanation exists, None otherwise
        """
        try:
            if not self.analytics_bucket:
                logger.warning("Analytics bucket not configured")
                return None
            
            # Try different possible file extensions
            possible_extensions = ['.html', '.htm']
            
            for ext in possible_extensions:
                s3_key = f"{self.explain_prefix}/{doc_id}{ext}"
                
                try:
                    # Check if file exists
                    self.s3_client.head_object(Bucket=self.analytics_bucket, Key=s3_key)
                    
                    # Generate pre-signed URL
                    url = get_s3_presigned_url(
                        self.s3_client,
                        self.analytics_bucket,
                        s3_key,
                        expiration=600  # 10 minutes
                    )
                    
                    logger.info(f"Found pre-computed explanation for doc_id: {doc_id}")
                    return url
                    
                except self.s3_client.exceptions.NoSuchKey:
                    continue
                except Exception as e:
                    logger.error(f"Error checking S3 for {s3_key}: {str(e)}")
                    continue
            
            logger.info(f"No pre-computed explanation found for doc_id: {doc_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get pre-computed explanation URL: {str(e)}")
            return None
    
    def _get_token_saliency(self, text: str, top_k: int) -> list:
        """Get token saliency scores using attention weights.
        
        Args:
            text: Input text
            top_k: Number of top tokens to return
            
        Returns:
            List of (token, saliency_score) tuples
        """
        try:
            # Use the model's token importance method
            token_importance = self.model.get_token_importance(text, top_k)
            
            if token_importance:
                return token_importance
            
            # Fallback: simple token-based approach
            return self._simple_token_saliency(text, top_k)
            
        except Exception as e:
            logger.error(f"Failed to get token saliency: {str(e)}")
            return self._simple_token_saliency(text, top_k)
    
    def _simple_token_saliency(self, text: str, top_k: int) -> list:
        """Simple token saliency based on word frequency and position.
        
        Args:
            text: Input text
            top_k: Number of top tokens to return
            
        Returns:
            List of (token, saliency_score) tuples
        """
        # Simple heuristic: longer words and words in middle positions are more important
        words = text.split()
        
        if not words:
            return []
        
        # Calculate simple saliency scores
        token_scores = []
        for i, word in enumerate(words):
            # Clean the word
            clean_word = ''.join(c for c in word if c.isalnum()).lower()
            if len(clean_word) < 3:  # Skip very short words
                continue
            
            # Score based on word length and position
            length_score = min(len(clean_word) / 10.0, 1.0)  # Normalize by max expected length
            position_score = 1.0 - abs(i - len(words) / 2) / (len(words) / 2)  # Middle words get higher score
            
            total_score = (length_score + position_score) / 2
            token_scores.append((clean_word, total_score))
        
        # Sort by score and return top_k
        token_scores.sort(key=lambda x: x[1], reverse=True)
        return token_scores[:top_k]
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence score to human-readable level.
        
        Args:
            confidence: Confidence score (0-1)
            
        Returns:
            Confidence level string
        """
        if confidence >= 0.9:
            return "very_high"
        elif confidence >= 0.8:
            return "high"
        elif confidence >= 0.7:
            return "medium_high"
        elif confidence >= 0.6:
            return "medium"
        elif confidence >= 0.5:
            return "medium_low"
        else:
            return "low"
    
    def _fallback_explanation(self, text: str, doc_id: Optional[str] = None) -> Dict[str, Any]:
        """Provide a fallback explanation when the main method fails.
        
        Args:
            text: Input text
            doc_id: Optional document ID
            
        Returns:
            Fallback explanation dictionary
        """
        # Simple keyword-based fallback
        high_risk_keywords = [
            "indemnify", "indemnification", "liability", "damages", 
            "breach", "terminate", "penalty", "fine", "compensation",
            "warranty", "guarantee", "assurance", "obligation"
        ]
        
        text_lower = text.lower()
        
        # Find keywords in text
        found_keywords = [kw for kw in high_risk_keywords if kw in text_lower][:5]
        
        return {
            "type": "tokens",
            "top_terms": found_keywords,
            "token_saliency": {term: 1.0 for term in found_keywords},
            "prediction_direction": "unknown",
            "confidence_level": "low",
            "html_url": None,
            "explanation_method": "keyword_fallback",
            "has_precomputed": False,
            "doc_id": doc_id
        }
    
    def list_available_explanations(self, prefix: str = "") -> Dict[str, Any]:
        """List available pre-computed explanations in S3.
        
        Args:
            prefix: Optional prefix to filter by
            
        Returns:
            Dictionary with list of available explanations
        """
        try:
            if not self.analytics_bucket:
                return {"error": "Analytics bucket not configured"}
            
            # List objects in the explain prefix
            s3_prefix = f"{self.explain_prefix}/{prefix}" if prefix else self.explain_prefix
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.analytics_bucket,
                Prefix=s3_prefix,
                MaxKeys=100  # Limit results
            )
            
            if 'Contents' not in response:
                return {"explanations": [], "count": 0}
            
            explanations = []
            for obj in response['Contents']:
                # Extract doc_id from key
                key = obj['Key']
                if key.endswith('.html') or key.endswith('.htm'):
                    doc_id = key.replace(f"{self.explain_prefix}/", "").replace('.html', '').replace('.htm', '')
                    explanations.append({
                        "doc_id": doc_id,
                        "s3_key": key,
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'].isoformat()
                    })
            
            return {
                "explanations": explanations,
                "count": len(explanations),
                "bucket": self.analytics_bucket,
                "prefix": s3_prefix
            }
            
        except Exception as e:
            logger.error(f"Failed to list available explanations: {str(e)}")
            return {"error": str(e)}
