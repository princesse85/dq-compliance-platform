#!/usr/bin/env python3
"""
Test Dashboard Data Integration

This script tests that the dashboard can load and display real compliance data.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_dashboard_data():
    """Test that dashboard can load real compliance data."""
    print("Testing Dashboard Data Integration...")
    print("=" * 50)
    
    try:
        # Test real compliance data loading
        from dashboard.real_ml_utils import get_real_compliance_data
        
        real_data = get_real_compliance_data()
        
        if not real_data.empty:
            print(f"[OK] Real compliance data loaded: {len(real_data)} records")
            print(f"  Categories: {real_data['Risk Category'].unique().tolist()}")
            print(f"  Risk Levels: {real_data['Risk Level'].unique().tolist()}")
            print(f"  Date range: {real_data['Date'].min()} to {real_data['Date'].max()}")
        else:
            print("[WARNING] No real compliance data found, dashboard will use mock data")
        
        # Test dashboard data loader
        from dashboard.utils import DashboardDataLoader
        
        data_loader = DashboardDataLoader()
        
        # Test loading current year data
        from datetime import datetime
        current_year = datetime.now().year
        
        dashboard_data = data_loader.load_compliance_data(current_year)
        print(f"\n[OK] Dashboard data loaded: {len(dashboard_data)} records")
        
        # Test filtering
        financial_data = data_loader.load_compliance_data(current_year, 'financial')
        print(f"[OK] Financial risk data: {len(financial_data)} records")
        
        # Test compliance score
        compliance_score = data_loader.fetch_compliance_score(current_year)
        print(f"[OK] Compliance score for {current_year}: {compliance_score}%")
        
        # Test risk trends
        trends = data_loader.get_risk_trends(current_year)
        print(f"[OK] Risk trends data: {len(trends)} records")
        
        print("\n" + "=" * 50)
        print("[SUCCESS] Dashboard Data Integration Test Completed!")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Dashboard data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dashboard_data()
    sys.exit(0 if success else 1)