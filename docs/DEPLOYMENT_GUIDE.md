# Enterprise Data Quality & Compliance Platform - Deployment Guide

This guide will help you deploy the Enterprise Data Quality & Compliance Platform to your own AWS account using your credentials.

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js 16+** - [Download here](https://nodejs.org/)
- **AWS CLI** - [Download here](https://aws.amazon.com/cli/)
- **Docker** (optional) - [Download here](https://www.docker.com/)

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/dq-compliance-platform.git
cd dq-compliance-platform
```

### Step 2: Configure AWS Credentials

Configure your AWS credentials using one of these methods:

#### Option A: AWS CLI Configuration
```bash
aws configure
```
Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Output format (json)

#### Option B: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

#### Option C: AWS Credentials File
Create `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key
```

### Step 3: Run the Setup Script

#### For Linux/macOS:
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh setup
```

#### For Windows:
```powershell
.\scripts\setup.ps1 setup
```

The setup script will:
- ✅ Check prerequisites
- ✅ Validate AWS credentials
- ✅ Install Python dependencies
- ✅ Install AWS CDK
- ✅ Configure environment
- ✅ Bootstrap CDK

### Step 4: Deploy Infrastructure

```bash
# Linux/macOS
./scripts/setup.sh deploy

# Windows
.\scripts\setup.ps1 deploy
```

This will deploy all AWS infrastructure stacks:
- **Foundation Stack** - S3 buckets, IAM roles, VPC
- **Billing Alarm Stack** - Cost monitoring and alerts
- **Data Quality Stack** - Great Expectations, Glue jobs
- **ML Inference Stack** - Lambda functions, API Gateway
- **Document Processing Stack** - Textract, OCR processing

## 📋 Detailed Setup Instructions

### 1. Environment Configuration

The setup script creates a `.env` file with your configuration:

```bash
# Environment Configuration
ENV_NAME=development
PROJECT_PREFIX=enterprise
AWS_REGION=us-east-1

# AWS Configuration
AWS_ACCOUNT_ID=123456789012

# Billing and Cost Management
BILLING_EMAIL=your-email@company.com
MONTHLY_BUDGET=5000

# Security (update these with your values)
AUTH_USER_POOL_ID=
AUTH_CLIENT_ID=
KMS_KEY_ALIAS=enterprise-development-key

# Monitoring
CLOUDWATCH_LOG_GROUP=/aws/enterprise-dq/development
```

### 2. Manual Setup (Alternative)

If you prefer manual setup:

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install CDK
npm install -g aws-cdk

# 5. Bootstrap CDK
cdk bootstrap

# 6. Deploy stacks
cdk deploy --all --require-approval never
```

### 3. Security Configuration

For production deployments, update the security settings in `.env`:

```bash
# Authentication (Cognito User Pool)
AUTH_USER_POOL_ID=us-east-1_xxxxxxxxx
AUTH_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx

# KMS Encryption
KMS_KEY_ALIAS=enterprise-production-key
```

## 🏗️ Infrastructure Components

### Foundation Stack
- **S3 Buckets**: Data lake, processed data, analytics
- **IAM Roles**: Service roles and permissions
- **VPC**: Network isolation and security
- **CloudWatch**: Logging and monitoring

### Billing Alarm Stack
- **CloudWatch Alarms**: Cost monitoring
- **SNS Topics**: Alert notifications
- **Budget Tracking**: Monthly spending limits

### Data Quality Stack
- **Great Expectations**: Data validation framework
- **AWS Glue**: ETL jobs and data processing
- **Data Quality Dashboard**: Validation results

### ML Inference Stack
- **Lambda Functions**: Model inference API
- **API Gateway**: REST API endpoints
- **Model Registry**: MLflow model management

### Document Processing Stack
- **Amazon Textract**: OCR and document analysis
- **S3 Processing**: Document storage and retrieval
- **Lambda Handlers**: Document processing workflows

## 🔧 Configuration Options

### Environment Variables

You can customize the deployment using environment variables:

```bash
# Project configuration
export PROJECT_PREFIX=mycompany
export ENV_NAME=production
export AWS_REGION=eu-west-1

# Billing configuration
export BILLING_EMAIL=billing@mycompany.com
export MONTHLY_BUDGET=10000

# Security configuration
export AUTH_USER_POOL_ID=eu-west-1_xxxxxxxxx
export AUTH_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
export KMS_KEY_ALIAS=mycompany-production-key
```

### CDK Context

You can also use CDK context for configuration:

```bash
cdk deploy --context env_name=production --context project_prefix=mycompany
```

## 🧪 Testing Your Deployment

### 1. Run Tests
```bash
# Linux/macOS
./scripts/setup.sh test

# Windows
.\scripts\setup.ps1 test
```

### 2. Test API Endpoints
```bash
# Get API Gateway URL from CDK outputs
cdk deploy --outputs-file outputs.json

# Test health endpoint
curl https://your-api-gateway-url.amazonaws.com/prod/health

# Test prediction endpoint
curl -X POST https://your-api-gateway-url.amazonaws.com/prod/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test document", "model": "baseline"}'
```

### 3. Monitor Resources
- **CloudWatch**: View logs and metrics
- **S3 Console**: Check data lake buckets
- **Lambda Console**: Monitor function performance
- **API Gateway**: View API usage and errors

## 🔍 Troubleshooting

### Common Issues

#### 1. AWS Credentials Not Found
```bash
# Verify credentials
aws sts get-caller-identity

# Reconfigure if needed
aws configure
```

#### 2. CDK Bootstrap Required
```bash
# Bootstrap CDK
cdk bootstrap

# Verify bootstrap
aws cloudformation describe-stacks --stack-name CDKToolkit
```

#### 3. Insufficient Permissions
Ensure your AWS user/role has these permissions:
- CloudFormation (Full Access)
- S3 (Full Access)
- IAM (Limited - for service roles)
- Lambda (Full Access)
- API Gateway (Full Access)
- CloudWatch (Full Access)
- KMS (Limited - for encryption keys)

#### 4. Python Dependencies Issues
```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### 5. CDK Version Mismatch
```bash
# Update CDK
npm update -g aws-cdk

# Verify version
cdk --version
```

### Getting Help

1. **Check Logs**: Review CloudWatch logs for detailed error messages
2. **CDK Diff**: See what changes will be made: `cdk diff`
3. **Destroy and Redeploy**: `cdk destroy --all && cdk deploy --all`
4. **GitHub Issues**: Report bugs and request features

## 🚀 Production Deployment

### 1. Environment Separation
```bash
# Development
cdk deploy --context env_name=development

# Staging
cdk deploy --context env_name=staging

# Production
cdk deploy --context env_name=production
```

### 2. Security Hardening
- Enable AWS Config for compliance monitoring
- Set up CloudTrail for audit logging
- Configure VPC endpoints for private access
- Enable encryption at rest and in transit
- Set up proper IAM roles and policies

### 3. Monitoring and Alerting
- Configure CloudWatch dashboards
- Set up SNS notifications for critical events
- Enable AWS Health monitoring
- Set up cost anomaly detection

### 4. Backup and Recovery
- Enable S3 versioning for data protection
- Set up cross-region replication
- Configure automated backups
- Test disaster recovery procedures

## 📊 Cost Optimization

### Estimated Costs (Monthly)
- **Development**: $50-200
- **Staging**: $100-500
- **Production**: $500-2000

### Cost Optimization Tips
1. **Use Spot Instances**: For non-critical workloads
2. **S3 Lifecycle Policies**: Move old data to cheaper storage
3. **Lambda Optimization**: Optimize function memory and timeout
4. **CloudWatch Logs**: Set retention policies
5. **Reserved Instances**: For predictable workloads

## 🔄 Updates and Maintenance

### Updating the Platform
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Deploy updates
cdk deploy --all
```

### Monitoring and Maintenance
- **Weekly**: Review CloudWatch metrics and logs
- **Monthly**: Check cost reports and optimize
- **Quarterly**: Update dependencies and security patches
- **Annually**: Review architecture and plan improvements

## 📞 Support

For additional support:
- **Documentation**: Check the `docs/` directory
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the development team

---

**🎉 Congratulations!** Your Enterprise Data Quality & Compliance Platform is now deployed and ready to use!
