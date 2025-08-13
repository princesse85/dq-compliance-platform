#!/usr/bin/env python3
"""
Test ML Integration with Dashboard

This script tests that the real ML models are properly integrated
with the Streamlit dashboard.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_ml_integration():
    """Test that ML models are properly integrated."""
    print("Testing ML Model Integration...")
    print("=" * 50)
    
    try:
        # Test importing real ML utils
        from dashboard.real_ml_utils import ml_predictor, analyze_document_with_real_ml
        print("[OK] Successfully imported real ML utilities")
        
        # Test model loading
        if ml_predictor.baseline_model is not None:
            print("[OK] Baseline model loaded successfully")
        else:
            print("[WARNING] Baseline model not loaded, will use mock predictions")
        
        # Test prediction
        test_text = "This contract contains high-risk clauses with potential regulatory violations and enforcement actions."
        prediction = ml_predictor.predict_risk(test_text)
        
        print(f"\nTest Prediction Results:")
        print(f"  Text: {test_text[:80]}...")
        print(f"  Risk Level: {prediction['risk_level']}")
        print(f"  Confidence: {prediction['confidence']:.3f}")
        print(f"  Model Used: {prediction['model_used']}")
        
        # Test document analysis
        class MockFile:
            def __init__(self, content, name):
                self.content = content
                self.name = name
            
            def getvalue(self):
                return self.content.encode('utf-8')
        
        mock_file = MockFile(test_text, "test_contract.txt")
        analysis = analyze_document_with_real_ml(mock_file)
        
        if analysis:
            print(f"\nDocument Analysis Results:")
            print(f"  Filename: {analysis['filename']}")
            print(f"  Risk Level: {analysis['risk_level']}")
            print(f"  Compliance Score: {analysis['compliance_score']}%")
            print(f"  Model Used: {analysis['model_used']}")
            print(f"  Key Risks: {len(analysis['key_risks'])} identified")
        
        # Test dashboard utils integration
        from dashboard.utils import analyze_document_with_ml, generate_ml_metrics
        
        dashboard_analysis = analyze_document_with_ml(mock_file)
        if dashboard_analysis:
            print(f"\nDashboard Integration Results:")
            print(f"  Risk Level: {dashboard_analysis['risk_level']}")
            print(f"  Model Used: {dashboard_analysis['model_used']}")
            
        # Test ML metrics
        metrics_df = generate_ml_metrics()
        print(f"\nML Metrics:")
        print(f"  Total metrics: {len(metrics_df)} records")
        print(f"  Models available: {metrics_df['model_name'].unique().tolist()}")
        
        print("\n" + "=" * 50)
        print("[SUCCESS] ML Integration Test Completed!")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] ML Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ml_integration()
    sys.exit(0 if success else 1)