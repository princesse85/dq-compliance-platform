import logging
import re
from typing import Dict, Any, List, Tuple
from .load_baseline import BaselineModel

logger = logging.getLogger(__name__)

class BaselineExplainer:
    """Explainer for baseline TF-IDF + Logistic Regression model."""
    
    def __init__(self, model: BaselineModel):
        """Initialize the explainer with a baseline model.
        
        Args:
            model: Loaded BaselineModel instance
        """
        self.model = model
    
    def explain(self, text: str, top_n: int = 5) -> Dict[str, Any]:
        """Generate explanation for the baseline model prediction.
        
        Args:
            text: Input text to explain
            top_n: Number of top terms to return
            
        Returns:
            Dictionary containing explanation details
        """
        try:
            # Get feature coefficients from the model
            feature_coeffs = self.model.get_coefficients()
            
            if not feature_coeffs:
                return self._fallback_explanation(text)
            
            # Extract important terms from the text
            important_terms = self._extract_important_terms(text, feature_coeffs, top_n)
            
            # Get prediction details
            prediction = self.model.predict(text)
            confidence = self.model.predict_proba(text)
            
            # Determine if prediction is high risk
            is_high_risk = prediction == "HighRisk"
            
            # Filter terms based on prediction direction
            if is_high_risk:
                # For high risk, show terms that contribute positively
                relevant_terms = [term for term, coeff in important_terms if coeff > 0]
            else:
                # For low risk, show terms that contribute negatively (or are missing)
                relevant_terms = [term for term, coeff in important_terms if coeff < 0]
            
            # If no relevant terms found, use top terms by absolute coefficient
            if not relevant_terms:
                relevant_terms = [term for term, _ in important_terms[:top_n]]
            
            return {
                "type": "tokens",
                "top_terms": relevant_terms[:top_n],
                "coefficients": {term: coeff for term, coeff in important_terms[:top_n]},
                "prediction_direction": "high_risk" if is_high_risk else "low_risk",
                "confidence_level": self._get_confidence_level(confidence),
                "html_url": None,  # Baseline doesn't have pre-computed HTML
                "explanation_method": "tfidf_coefficients"
            }
            
        except Exception as e:
            logger.error(f"Baseline explanation failed: {str(e)}")
            return self._fallback_explanation(text)
    
    def _extract_important_terms(self, text: str, feature_coeffs: List[Tuple[str, float]], top_n: int) -> List[Tuple[str, float]]:
        """Extract important terms from text based on model coefficients.
        
        Args:
            text: Input text
            feature_coeffs: List of (feature, coefficient) tuples
            top_n: Number of top terms to return
            
        Returns:
            List of (term, coefficient) tuples found in the text
        """
        # Convert text to lowercase for matching
        text_lower = text.lower()
        
        # Find terms that appear in the text
        found_terms = []
        for feature, coeff in feature_coeffs:
            # Check if the feature appears in the text
            if self._term_in_text(feature, text_lower):
                found_terms.append((feature, coeff))
        
        # Sort by absolute coefficient value
        found_terms.sort(key=lambda x: abs(x[1]), reverse=True)
        
        return found_terms[:top_n]
    
    def _term_in_text(self, term: str, text_lower: str) -> bool:
        """Check if a term appears in the text.
        
        Args:
            term: Term to search for
            text_lower: Lowercase text to search in
            
        Returns:
            True if term is found in text
        """
        # Handle multi-word terms
        if ' ' in term:
            return term in text_lower
        
        # For single words, use word boundaries
        pattern = r'\b' + re.escape(term) + r'\b'
        return bool(re.search(pattern, text_lower))
    
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
    
    def _fallback_explanation(self, text: str) -> Dict[str, Any]:
        """Provide a fallback explanation when the main method fails.
        
        Args:
            text: Input text
            
        Returns:
            Fallback explanation dictionary
        """
        # Simple keyword-based fallback
        high_risk_keywords = [
            "indemnify", "indemnification", "liability", "damages", 
            "breach", "terminate", "penalty", "fine", "compensation",
            "warranty", "guarantee", "assurance", "obligation"
        ]
        
        low_risk_keywords = [
            "standard", "normal", "usual", "typical", "routine",
            "basic", "simple", "standard", "conventional"
        ]
        
        text_lower = text.lower()
        
        # Count keyword occurrences
        high_risk_count = sum(1 for keyword in high_risk_keywords if keyword in text_lower)
        low_risk_count = sum(1 for keyword in low_risk_keywords if keyword in text_lower)
        
        # Determine top terms based on keyword presence
        if high_risk_count > low_risk_count:
            top_terms = [kw for kw in high_risk_keywords if kw in text_lower][:3]
        else:
            top_terms = [kw for kw in low_risk_keywords if kw in text_lower][:3]
        
        return {
            "type": "tokens",
            "top_terms": top_terms,
            "coefficients": {term: 1.0 for term in top_terms},
            "prediction_direction": "unknown",
            "confidence_level": "low",
            "html_url": None,
            "explanation_method": "keyword_fallback"
        }
    
    def get_feature_importance_summary(self) -> Dict[str, Any]:
        """Get a summary of the most important features in the model.
        
        Returns:
            Dictionary with feature importance summary
        """
        try:
            feature_coeffs = self.model.get_coefficients()
            
            if not feature_coeffs:
                return {"error": "No feature coefficients available"}
            
            # Get top positive and negative coefficients
            positive_terms = [(term, coeff) for term, coeff in feature_coeffs if coeff > 0][:10]
            negative_terms = [(term, coeff) for term, coeff in feature_coeffs if coeff < 0][:10]
            
            return {
                "top_positive_features": positive_terms,
                "top_negative_features": negative_terms,
                "total_features": len(feature_coeffs),
                "model_type": "tfidf_logistic_regression"
            }
            
        except Exception as e:
            logger.error(f"Failed to get feature importance summary: {str(e)}")
            return {"error": str(e)}
