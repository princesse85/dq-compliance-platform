
import os
from dotenv import load_dotenv

load_dotenv()

class StagingConfig:
    """
    Configuration settings for the staging environment.
    """
    ENV_NAME = "staging"
    AWS_REGION = os.getenv("AWS_STAGING_REGION", "eu-west-2")
    PROJECT_PREFIX = "dq-platform"
    BILLING_EMAIL = os.getenv("STAGING_BILLING_EMAIL", "your-staging-email@example.com")
    MONTHLY_BUDGET = 2500
    
    # You can add other staging-specific configurations here
    # For example, smaller instance types, different feature flags, etc.

    def __init__(self):
        # You can add any logic here to derive or validate configurations
        pass

    def get_stack_name(self, stack_name):
        """
        Get the full stack name with prefix and environment.
        """
        return f"{self.PROJECT_PREFIX}-{self.ENV_NAME}-{stack_name}"

    def get_resource_name(self, resource_name):
        """
        Get a unique resource name with prefix and environment.
        """
        return f"{self.PROJECT_PREFIX}-{self.ENV_NAME}-{resource_name}"

