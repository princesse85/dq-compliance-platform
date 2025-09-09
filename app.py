#!/usr/bin/env python3
import os
import aws_cdk as cdk
from infrastructure.ecr_stack import EcrStack
from infrastructure.main_stack import MainStack
from infrastructure.production import ProductionConfig
from infrastructure.staging import StagingConfig

app = cdk.App()

# Load configuration based on environment
env_name = app.node.try_get_context("env_name")
if env_name == "staging":
    config = StagingConfig()
elif env_name == "production":
    config = ProductionConfig()
else:
    raise ValueError(f"Invalid environment name: {env_name}. Must be 'staging' or 'production'.")

project_prefix = config.PROJECT_PREFIX
region = config.AWS_REGION
billing_email = config.BILLING_EMAIL
monthly_budget = config.MONTHLY_BUDGET

# Define environment for the stack
aws_env = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=region)

# Instantiate the ECR stack
ecr_stack = EcrStack(app, f"{project_prefix}-{env_name}-EcrStack",
                     env=aws_env,
                     project_prefix=project_prefix,
                     env_name=env_name)

# Instantiate the main stack
main_stack = MainStack(app, f"{project_prefix}-{env_name}-MainStack",
                           env=aws_env,
                           project_prefix=project_prefix,
                           env_name=env_name,
                           billing_email=billing_email,
                           monthly_budget=monthly_budget,
                           ecr_repo=ecr_stack.ecr_repo)

app.synth()
