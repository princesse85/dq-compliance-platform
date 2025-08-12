import os
import aws_cdk as cdk
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from infrastructure.foundation_stack import FoundationStack
from infrastructure.billing_alarm_stack import BillingAlarmStack
from infrastructure.data_quality_stack import DataQualityStack
from infrastructure.ml_inference_stack import MLInferenceStack
from infrastructure.document_processing_stack import DocumentProcessingStack

app = cdk.App()

# Configuration from environment variables and context
project_prefix = os.getenv("PROJECT_PREFIX") or app.node.try_get_context("project_prefix") or "enterprise"
env_name = os.getenv("ENV_NAME") or app.node.try_get_context("env_name") or "development"
primary_region = os.getenv("AWS_REGION") or app.node.try_get_context("region") or os.getenv("CDK_DEFAULT_REGION") or "us-east-1"
billing_email = os.getenv("BILLING_EMAIL") or app.node.try_get_context("billing_email") or "enterprise-support@company.com"
monthly_budget = float(os.getenv("MONTHLY_BUDGET") or app.node.try_get_context("monthly_budget") or 5000)

# Environment configurations
primary_env = cdk.Environment(account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=primary_region)
us_east_1_env = cdk.Environment(account=os.getenv("CDK_DEFAULT_ACCOUNT"), region="us-east-1")

# Foundation Infrastructure Stack
foundation = FoundationStack(
    app,
    f"{project_prefix}-foundation",
    project_prefix=project_prefix,
    env_name=env_name,
    billing_email=billing_email,
    monthly_budget=monthly_budget,
    env=primary_env,
)

# Billing Alarm Stack (us-east-1 required for billing metrics)
billing = BillingAlarmStack(
    app,
    f"{project_prefix}-billing",
    billing_email=billing_email,
    monthly_budget=monthly_budget,
    env=us_east_1_env,
)

# Data Quality Platform Stack
data_quality = DataQualityStack(
    app,
    f"{project_prefix}-data-quality",
    project_prefix=project_prefix,
    env_name=env_name,
    env=primary_env,
)

# Machine Learning Inference Stack
ml_inference = MLInferenceStack(
    app,
    f"{project_prefix}-ml-inference",
    project_prefix=project_prefix,
    env_name=env_name,
    analytics_bucket=foundation.analytics_bucket,
    env=primary_env,
)

# Document Processing Stack
document_processing = DocumentProcessingStack(
    app,
    f"{project_prefix}-document-processing",
    project_prefix=project_prefix,
    env_name=env_name,
    env=primary_env,
)

# Add tags for resource management
for stack in [foundation, billing, data_quality, ml_inference]:
    cdk.Tags.of(stack).add("Project", "EnterpriseDataQuality")
    cdk.Tags.of(stack).add("Environment", env_name)
    cdk.Tags.of(stack).add("ManagedBy", "CDK")
    cdk.Tags.of(stack).add("CostCenter", "DataPlatform")

app.synth()
