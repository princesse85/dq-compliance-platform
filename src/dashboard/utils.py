"""
Dashboard utility functions for data loading, processing, and visualization.
"""

import pandas as pd
import numpy as np
import boto3
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from .real_ml_utils import analyze_document_with_real_ml, get_real_ml_metrics, get_real_compliance_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardDataLoader:
    """Handles data loading and processing for the dashboard."""

    def __init__(self, aws_region: str = "us-east-1"):
        self.aws_region = aws_region
        self.s3_client = None
        self._initialize_aws_client()

    def _initialize_aws_client(self):
        """Initialize AWS S3 client."""
        try:
            # Only try to initialize if we have valid AWS credentials
            if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
                self.s3_client = boto3.client("s3", region_name=self.aws_region)
                # Test the credentials with a simple call
                try:
                    self.s3_client.list_buckets()
                    logger.info("AWS S3 client initialized successfully")
                except Exception as e:
                    if "InvalidAccessKeyId" in str(e) or "SignatureDoesNotMatch" in str(e):
                        logger.info("AWS credentials found but invalid - using local data only")
                        self.s3_client = None
                    else:
                        raise e
            else:
                self.s3_client = None
        except Exception as e:
            # Don't log warnings for missing credentials (expected in demo)
            if "NoCredentialsError" not in str(e) and "InvalidAccessKeyId" not in str(e):
                logger.warning(f"Failed to initialize AWS S3 client: {e}")
            self.s3_client = None

    def load_compliance_data(self, year: int, risk_type: str = "all") -> pd.DataFrame:
        """
        Load compliance data from S3 or generate mock data.

        Args:
            year: Year for data retrieval
            risk_type: Type of risk to filter

        Returns:
            DataFrame with compliance data
        """
        try:
            # Try to load from S3 first
            if self.s3_client:
                return self._load_from_s3(year, risk_type)
            else:
                return self._generate_mock_data(year, risk_type)
        except Exception as e:
            logger.error(f"Error loading compliance data: {e}")
            return self._generate_mock_data(year, risk_type)

    def _load_from_s3(self, year: int, risk_type: str) -> pd.DataFrame:
        """Load data from S3 bucket."""
        bucket_name = os.getenv("COMPLIANCE_BUCKET", "enterprise-analytics-production")
        file_key = f"compliance_data/{year}/{risk_type.lower()}_risks.csv"

        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=file_key)
            data = pd.read_csv(response["Body"])
            logger.info(f"Successfully loaded data from S3: {file_key}")
            return data
        except Exception as e:
            # Only log warning if we have S3 credentials but bucket doesn't exist
            if "NoSuchBucket" in str(e) or "AccessDenied" in str(e):
                logger.info(f"Using mock data (S3 bucket not available): {bucket_name}")
            else:
                logger.warning(f"Failed to load from S3: {e}")
            return self._generate_mock_data(year, risk_type)

    def _generate_mock_data(self, year: int, risk_type: str) -> pd.DataFrame:
        """Generate mock compliance data for demonstration, with real data when available."""
        # First try to get real compliance data
        try:
            real_data = get_real_compliance_data()
            if not real_data.empty:
                logger.info(f"Using real compliance data ({len(real_data)} records)")
                # Filter by year if needed
                real_data['Date'] = pd.to_datetime(real_data['Date'])
                real_data = real_data[real_data['Date'].dt.year == year]
                
                if risk_type != 'all':
                    real_data = real_data[real_data['Risk Category'].str.lower() == risk_type.lower()]
                
                return real_data
        except Exception as e:
            logger.warning(f"Could not load real data, using mock: {e}")
        
        # Fallback to mock data
        np.random.seed(year)
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        dates = pd.to_datetime([start_date + timedelta(days=i) for i in range(365)])
        
        data = []
        risk_categories = ["Financial", "Operational", "Legal", "Regulatory", "Cybersecurity"]
        regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
        
        for date in dates:
            for _ in range(np.random.randint(5, 15)):
                category = np.random.choice(risk_categories)
                region = np.random.choice(regions)
                risk_value = np.random.uniform(20, 95)
                
                if risk_value > 80:
                    level = "High"
                elif risk_value > 50:
                    level = "Medium"
                else:
                    level = "Low"
                    
                data.append({
                    "Date": date,
                    "Risk Category": category,
                    "Region": region,
                    "Risk Value": risk_value,
                    "Risk Level": level,
                    "ID": f"RISK-{np.random.randint(10000, 99999)}"
                })
                
        df = pd.DataFrame(data)
        if risk_type != 'all':
            df = df[df['Risk Category'].str.lower() == risk_type]
        return df

    def fetch_compliance_score(self, year: int) -> float:
        """Fetch overall compliance score for a given year."""
        np.random.seed(year)
        return round(np.random.uniform(85.0, 98.0), 1)
        
    def get_risk_trends(self, year: int) -> pd.DataFrame:
        """Get risk trends over time for a given year."""
        data = self.load_compliance_data(year)
        trends = data.groupby([pd.Grouper(key='Date', freq='ME'), 'Risk Category'])['Risk Value'].mean().reset_index()
        return trends


def format_number(n: int) -> str:
    """Format a number with commas."""
    return f"{n:,}"


def generate_ml_metrics() -> pd.DataFrame:
    """Generate ML model metrics with real data when available."""
    try:
        # Try to get real ML metrics first
        real_metrics = get_real_ml_metrics()
        if not real_metrics.empty:
            logger.info(f"Using real ML metrics ({len(real_metrics)} records)")
            return real_metrics
    except Exception as e:
        logger.warning(f"Could not load real ML metrics, using mock: {e}")
    
    # Fallback to mock metrics
    models = ["legal-bert-v2.1", "compliance-gpt-3.5", "risk-detector-xlnet"]
    metrics_data = []
    for model in models:
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            metrics_data.append({
                "date": date,
                "model_name": model,
                "accuracy": np.random.uniform(0.88, 0.95) - (i * 0.0005),
                "precision": np.random.uniform(0.85, 0.96) - (i * 0.0004),
                "recall": np.random.uniform(0.87, 0.97) - (i * 0.0006),
                "latency_ms": np.random.uniform(150, 450) + (i * 1.2),
            })
    return pd.DataFrame(metrics_data)


def get_data_quality_metrics() -> Dict:
    """Get data quality metrics."""
    metrics = {
        "Overall Score": {"value": 96.2, "delta": 1.1},
        "Completeness": {"value": 98.1, "delta": 0.5},
        "Uniqueness": {"value": 99.5, "delta": -0.1},
        "Timeliness": {"value": 92.5, "delta": 2.3},
        "Validity": {"value": 97.8, "delta": -0.2},
        "Accuracy": {"value": 93.1, "delta": 1.5},
    }
    return metrics


def analyze_document_with_ml(uploaded_file) -> Optional[Dict]:
    """Analyze document using real ML models."""
    if uploaded_file is None:
        return None

    try:
        # Try to use real ML analysis first
        real_analysis = analyze_document_with_real_ml(uploaded_file)
        if real_analysis:
            logger.info(f"Using real ML analysis for document: {real_analysis.get('filename', 'unknown')}")
            return real_analysis
    except Exception as e:
        logger.warning(f"Real ML analysis failed, using fallback: {e}")

    # Fallback to mock analysis
    try:
        analysis = {
            "filename": uploaded_file.name,
            "file_size": len(uploaded_file.getvalue()),
            "compliance_score": np.random.randint(75, 95),
            "risk_level": np.random.choice(["Low", "Medium", "High"], p=[0.6, 0.3, 0.1]),
            "confidence": np.random.uniform(0.85, 0.98),
            "processing_time": np.random.uniform(0.2, 0.8),
            "key_risks": [
                "Regulatory compliance gaps identified",
                "Contract clause ambiguity detected",
                "Data privacy considerations noted"
            ],
            "recommendations": [
                "Review Section 4.2 for compliance requirements",
                "Clarify terms in paragraphs 7-9",
                "Add data protection clauses"
            ],
            "sentiment": {
                "positive": 0.65,
                "neutral": 0.25,
                "negative": 0.10
            },
            "entities": ["Company Name", "Contract Date", "Liability Terms"],
            "model_used": "mock_fallback"
        }
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        return None


