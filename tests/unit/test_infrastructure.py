import pytest
import boto3
from unittest.mock import Mock, patch, MagicMock
from aws_cdk import App, Environment
from aws_cdk.assertions import Template, Match

from infrastructure.foundation_stack import FoundationStack
from infrastructure.data_quality_stack import DataQualityStack
from infrastructure.ml_inference_stack import MLInferenceStack
from infrastructure.document_processing_stack import DocumentProcessingStack
from infrastructure.billing_alarm_stack import BillingAlarmStack
from infrastructure.security_config import SecurityConfig


class TestFoundationStack:
    """Unit tests for FoundationStack"""
    
    def test_foundation_stack_creation(self):
        """Test FoundationStack creates expected resources"""
        app = App()
        stack = FoundationStack(
            app, "test-foundation",
            project_prefix="test",
            env_name="test",
            billing_email="test@example.com",
            monthly_budget=1000,
            env=Environment(account="123456789012", region="us-east-1")
        )
        
        template = Template.from_stack(stack)
        
        # Verify S3 bucket creation
        template.has_resource_properties("AWS::S3::Bucket", {
            "BucketName": Match.string_like_regexp("test-analytics-*"),
            "VersioningConfiguration": {"Status": "Enabled"},
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "BlockPublicPolicy": True,
                "IgnorePublicAcls": True,
                "RestrictPublicBuckets": True
            }
        })
        
        # Verify IAM roles
        template.has_resource("AWS::IAM::Role", {})
        
        # Verify VPC creation
        template.has_resource("AWS::EC2::VPC", {})
    
    def test_foundation_stack_with_invalid_budget(self):
        """Test FoundationStack with invalid budget raises error"""
        app = App()
        
        with pytest.raises(ValueError):
            FoundationStack(
                app, "test-foundation",
                project_prefix="test",
                env_name="test",
                billing_email="test@example.com",
                monthly_budget=-100,  # Invalid negative budget
                env=Environment(account="123456789012", region="us-east-1")
            )


class TestDataQualityStack:
    """Unit tests for DataQualityStack"""
    
    def test_data_quality_stack_creation(self):
        """Test DataQualityStack creates expected resources"""
        app = App()
        stack = DataQualityStack(
            app, "test-data-quality",
            project_prefix="test",
            env_name="test",
            env=Environment(account="123456789012", region="us-east-1")
        )
        
        template = Template.from_stack(stack)
        
        # Verify Lambda functions
        template.has_resource("AWS::Lambda::Function", {})
        
        # Verify Step Functions
        template.has_resource("AWS::StepFunctions::StateMachine", {})
        
        # Verify CloudWatch alarms
        template.has_resource("AWS::CloudWatch::Alarm", {})


class TestMLInferenceStack:
    """Unit tests for MLInferenceStack"""
    
    def test_ml_inference_stack_creation(self):
        """Test MLInferenceStack creates expected resources"""
        app = App()
        mock_bucket = Mock()
        mock_bucket.bucket_name = "test-bucket"
        
        stack = MLInferenceStack(
            app, "test-ml-inference",
            project_prefix="test",
            env_name="test",
            analytics_bucket=mock_bucket,
            env=Environment(account="123456789012", region="us-east-1")
        )
        
        template = Template.from_stack(stack)
        
        # Verify SageMaker endpoints
        template.has_resource("AWS::SageMaker::Model", {})
        
        # Verify Lambda functions for inference
        template.has_resource("AWS::Lambda::Function", {})
        
        # Verify API Gateway
        template.has_resource("AWS::ApiGateway::RestApi", {})


class TestDocumentProcessingStack:
    """Unit tests for DocumentProcessingStack"""
    
    def test_document_processing_stack_creation(self):
        """Test DocumentProcessingStack creates expected resources"""
        app = App()
        stack = DocumentProcessingStack(
            app, "test-document-processing",
            project_prefix="test",
            env_name="test",
            env=Environment(account="123456789012", region="us-east-1")
        )
        
        template = Template.from_stack(stack)
        
        # Verify Textract resources
        template.has_resource("AWS::IAM::Role", {})
        
        # Verify S3 bucket for document storage
        template.has_resource("AWS::S3::Bucket", {})
        
        # Verify Lambda functions for processing
        template.has_resource("AWS::Lambda::Function", {})


class TestBillingAlarmStack:
    """Unit tests for BillingAlarmStack"""
    
    def test_billing_alarm_stack_creation(self):
        """Test BillingAlarmStack creates expected resources"""
        app = App()
        stack = BillingAlarmStack(
            app, "test-billing",
            billing_email="test@example.com",
            monthly_budget=1000,
            env=Environment(account="123456789012", region="us-east-1")
        )
        
        template = Template.from_stack(stack)
        
        # Verify CloudWatch billing alarm
        template.has_resource_properties("AWS::CloudWatch::Alarm", {
            "MetricName": "EstimatedCharges",
            "Namespace": "AWS/Billing",
            "ComparisonOperator": "GreaterThanThreshold"
        })
        
        # Verify SNS topic
        template.has_resource("AWS::SNS::Topic", {})


class TestSecurityConfig:
    """Unit tests for SecurityConfig"""
    
    def test_security_config_creation(self):
        """Test SecurityConfig creates expected security resources"""
        config = SecurityConfig()
        
        # Test VPC configuration
        vpc_config = config.create_vpc_config()
        assert vpc_config is not None
        assert "cidr" in vpc_config
        
        # Test IAM policies
        policies = config.create_iam_policies()
        assert isinstance(policies, dict)
        assert len(policies) > 0
        
        # Test security groups
        security_groups = config.create_security_groups()
        assert isinstance(security_groups, dict)
    
    def test_security_config_validation(self):
        """Test SecurityConfig validation methods"""
        config = SecurityConfig()
        
        # Test CIDR validation
        assert config.is_valid_cidr("10.0.0.0/16") == True
        assert config.is_valid_cidr("invalid-cidr") == False
        
        # Test port validation
        assert config.is_valid_port(80) == True
        assert config.is_valid_port(70000) == False
