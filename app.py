import os
import aws_cdk as cdk

from stacks.foundation_stack import FoundationStack
from stacks.billing_alarm_stack import BillingAlarmStack
from stacks.data_quality_stack import DataQualityStack
from stacks.ml_inference_stack import MLInferenceStack

app = cdk.App()

# Configuration from context
project_prefix = app.node.try_get_context("project_prefix") or "enterprise"
env_name = app.node.try_get_context("env_name") or "production"
primary_region = app.node.try_get_context("region") or os.getenv("CDK_DEFAULT_REGION") or "eu-west-2"
billing_email = app.node.try_get_context("billing_email") or "enterprise-support@company.com"
monthly_budget = float(app.node.try_get_context("monthly_budget") or 5000)

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

# Add tags for resource management
for stack in [foundation, billing, data_quality, ml_inference]:
    cdk.Tags.of(stack).add("Project", "EnterpriseDataQuality")
    cdk.Tags.of(stack).add("Environment", env_name)
    cdk.Tags.of(stack).add("ManagedBy", "CDK")
    cdk.Tags.of(stack).add("CostCenter", "DataPlatform")

app.synth()
