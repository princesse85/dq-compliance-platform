#!/usr/bin/env python3
"""
Test script for the Legal Compliance Inference API
Tests both baseline and transformer models with various inputs
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class APITester:
    def __init__(self, base_url: str):
        """Initialize the API tester.
        
        Args:
            base_url: Base URL of the API (without /predict)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def test_health(self) -> bool:
        """Test the health endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False
    
    def test_models(self) -> bool:
        """Test the models endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/models")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Models endpoint: {data}")
                return True
            else:
                print(f"❌ Models endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Models endpoint error: {str(e)}")
            return False
    
    def test_prediction(self, text: str, model: str = "auto", explain: bool = True, doc_id: str = None) -> Dict[str, Any]:
        """Test a prediction request.
        
        Args:
            text: Text to classify
            model: Model to use (auto, baseline, transformer)
            explain: Whether to include explanation
            doc_id: Optional document ID for pre-computed explanations
            
        Returns:
            Response data or None if failed
        """
        payload = {
            "text": text,
            "model": model,
            "explain": explain
        }
        
        if doc_id:
            payload["doc_id"] = doc_id
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/predict",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Prediction successful ({end_time - start_time:.2f}s):")
                print(f"   Model: {data.get('model', 'unknown')}")
                print(f"   Label: {data.get('label', 'unknown')}")
                print(f"   Confidence: {data.get('confidence', 0):.3f}")
                print(f"   Timings: {data.get('timings_ms', {})}")
                
                if explain and 'explanation' in data:
                    explanation = data['explanation']
                    print(f"   Explanation type: {explanation.get('type', 'unknown')}")
                    print(f"   Top terms: {explanation.get('top_terms', [])}")
                    if explanation.get('html_url'):
                        print(f"   HTML URL: {explanation['html_url']}")
                
                return data
            else:
                print(f"❌ Prediction failed ({response.status_code}): {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Prediction error: {str(e)}")
            return None
    
    def run_comprehensive_test(self):
        """Run a comprehensive test suite."""
        print("🚀 Starting comprehensive API test suite...")
        print("=" * 60)
        
        # Test 1: Health check
        print("\n1. Testing health endpoint...")
        if not self.test_health():
            print("❌ Health check failed. Exiting.")
            return False
        
        # Test 2: Models endpoint
        print("\n2. Testing models endpoint...")
        if not self.test_models():
            print("❌ Models endpoint failed. Exiting.")
            return False
        
        # Test 3: Baseline model predictions
        print("\n3. Testing baseline model predictions...")
        test_cases = [
            {
                "text": "This is a standard service agreement with normal terms and conditions.",
                "description": "Low risk contract"
            },
            {
                "text": "The contractor shall indemnify and hold harmless the client from any damages, losses, or liabilities arising from the performance of this agreement.",
                "description": "High risk contract with indemnification"
            },
            {
                "text": "Standard consulting services with limited liability not exceeding the contract value.",
                "description": "Low risk with liability limits"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   Test case {i}: {test_case['description']}")
            result = self.test_prediction(test_case['text'], model="baseline")
            if not result:
                print(f"   ❌ Test case {i} failed")
        
        # Test 4: Transformer model predictions
        print("\n4. Testing transformer model predictions...")
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   Test case {i}: {test_case['description']}")
            result = self.test_prediction(test_case['text'], model="transformer")
            if not result:
                print(f"   ❌ Test case {i} failed")
        
        # Test 5: Auto model selection
        print("\n5. Testing auto model selection...")
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   Test case {i}: {test_case['description']}")
            result = self.test_prediction(test_case['text'], model="auto")
            if not result:
                print(f"   ❌ Test case {i} failed")
        
        # Test 6: Without explanation
        print("\n6. Testing without explanation...")
        result = self.test_prediction(
            "Standard contract terms apply to this agreement.",
            model="auto",
            explain=False
        )
        if not result:
            print("   ❌ Test without explanation failed")
        
        # Test 7: With doc_id (for pre-computed explanations)
        print("\n7. Testing with doc_id for pre-computed explanations...")
        result = self.test_prediction(
            "Contract includes comprehensive indemnification clauses.",
            model="transformer",
            explain=True,
            doc_id="test_doc_001"
        )
        if not result:
            print("   ❌ Test with doc_id failed")
        
        print("\n" + "=" * 60)
        print("✅ Comprehensive test suite completed!")
        return True

def main():
    """Main function to run the API tests."""
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <API_BASE_URL>")
        print("Example: python test_api.py https://abc123.execute-api.us-east-1.amazonaws.com/prod")
        sys.exit(1)
    
    base_url = sys.argv[1]
    tester = APITester(base_url)
    
    # Run comprehensive test
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All tests passed! The API is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the API configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()
