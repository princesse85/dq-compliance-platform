#!/usr/bin/env python3
"""
Environment Configuration Script
Automatically configures the environment using AWS credentials and region.
"""

import os
import subprocess
import json
from pathlib import Path

def run_command(command, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def get_aws_identity():
    """Get AWS account identity."""
    success, output, error = run_command("aws sts get-caller-identity --query Account --output text")
    if success:
        return output
    return None

def get_aws_region():
    """Get configured AWS region."""
    success, output, error = run_command("aws configure get region")
    if success and output:
        return output
    return None

def get_aws_user():
    """Get AWS user/role name."""
    success, output, error = run_command("aws sts get-caller-identity --query Arn --output text")
    if success:
        # Extract user/role name from ARN
        parts = output.split('/')
        if len(parts) > 1:
            return parts[-1]
    return "unknown"

def create_env_file(project_prefix, billing_email, monthly_budget, aws_account_id, aws_region, aws_user):
    """Create .env file with configuration."""
    
    env_content = f"""# Environment Configuration
ENV_NAME=development
PROJECT_PREFIX={project_prefix}
AWS_REGION={aws_region}

# AWS Configuration
AWS_ACCOUNT_ID={aws_account_id}
AWS_USER={aws_user}

# Billing and Cost Management
BILLING_EMAIL={billing_email}
MONTHLY_BUDGET={monthly_budget}

# Security (update these with your values)
AUTH_USER_POOL_ID=
AUTH_CLIENT_ID=
KMS_KEY_ALIAS={project_prefix}-development-key

# Monitoring
CLOUDWATCH_LOG_GROUP=/aws/{project_prefix}-dq/development

# CDK Configuration
CDK_DEFAULT_ACCOUNT={aws_account_id}
CDK_DEFAULT_REGION={aws_region}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"✅ Environment configuration saved to .env")
    print(f"   Project Prefix: {project_prefix}")
    print(f"   AWS Region: {aws_region}")
    print(f"   AWS Account: {aws_account_id}")
    print(f"   Billing Email: {billing_email}")
    print(f"   Monthly Budget: ${monthly_budget}")

def main():
    """Main configuration function."""
    print("🔧 Enterprise Data Quality & Compliance Platform - Environment Configuration")
    print("=" * 70)
    
    # Check AWS credentials
    print("\n🔍 Checking AWS credentials...")
    success, output, error = run_command("aws sts get-caller-identity")
    if not success:
        print("❌ AWS credentials are not configured or invalid")
        print("Please configure your AWS credentials first:")
        print("  1. Run: aws configure")
        print("  2. Enter your AWS Access Key ID")
        print("  3. Enter your AWS Secret Access Key")
        print("  4. Enter your default region (e.g., us-east-1)")
        print("  5. Enter your output format (json)")
        return False
    
    # Get AWS information
    aws_account_id = get_aws_identity()
    aws_region = get_aws_region()
    aws_user = get_aws_user()
    
    if not aws_account_id:
        print("❌ Could not retrieve AWS account ID")
        return False
    
    if not aws_region:
        print("❌ AWS region not configured")
        print("Please run: aws configure")
        return False
    
    print(f"✅ AWS credentials validated successfully")
    print(f"   Account ID: {aws_account_id}")
    print(f"   Region: {aws_region}")
    print(f"   User: {aws_user}")
    
    # Get user input for configuration
    print("\n📝 Configuration Setup")
    print("-" * 30)
    
    project_prefix = input("Enter your project prefix (default: enterprise): ").strip()
    if not project_prefix:
        project_prefix = "enterprise"
    
    billing_email = input("Enter your billing email: ").strip()
    if not billing_email:
        print("❌ Billing email is required")
        return False
    
    monthly_budget = input("Enter your monthly budget in USD (default: 5000): ").strip()
    if not monthly_budget:
        monthly_budget = "5000"
    
    try:
        monthly_budget = float(monthly_budget)
    except ValueError:
        print("❌ Invalid monthly budget. Please enter a valid number.")
        return False
    
    # Create .env file
    print(f"\n📄 Creating environment configuration...")
    create_env_file(project_prefix, billing_email, monthly_budget, aws_account_id, aws_region, aws_user)
    
    print(f"\n🎉 Environment configuration completed successfully!")
    print(f"\nNext steps:")
    print(f"  1. Review the .env file and update security settings if needed")
    print(f"  2. Run: ./scripts/setup.sh deploy  (Linux/macOS)")
    print(f"  3. Run: .\\scripts\\deploy.ps1 deploy  (Windows)")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
