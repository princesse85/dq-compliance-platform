# Enterprise Data Quality & Compliance Platform - Deployment Guide

This guide provides comprehensive instructions for deploying the Enterprise Data Quality & Compliance Platform across different environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Local Development](#local-development)
4. [Staging Deployment](#staging-deployment)
5. [Production Deployment](#production-deployment)
6. [Monitoring and Observability](#monitoring-and-observability)
7. [Security Configuration](#security-configuration)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **AWS CLI**: [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- **AWS CDK**: `npm install -g aws-cdk`
- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Git**: [Install Git](https://git-scm.com/downloads)

### AWS Account Setup

1. **Create AWS Account**: [Sign up for AWS](https://aws.amazon.com/)
2. **Create IAM User**: Create a user with appropriate permissions
3. **Configure AWS CLI**:
   ```bash
   aws configure
   ```
4. **Set up AWS Credentials**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=eu-west-2
   ```

### Required AWS Permissions

Your IAM user/role needs the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "glue:*",
                "lambda:*",
                "iam:*",
                "cloudwatch:*",
                "logs:*",
                "ec2:*",
                "kms:*",
                "textract:*",
                "sagemaker:*",
                "apigateway:*",
                "cognito-idp:*"
            ],
            "Resource": "*"
        }
    ]
}
```

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd enterprise-data-quality-platform
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```bash
# Environment
ENV_NAME=development
PROJECT_PREFIX=enterprise
AWS_REGION=eu-west-2

# AWS Configuration
AWS_ACCOUNT_ID=your_account_id
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Billing and Cost Management
BILLING_EMAIL=your-email@company.com
MONTHLY_BUDGET=5000

# Security
AUTH_USER_POOL_ID=your_user_pool_id
AUTH_CLIENT_ID=your_client_id
KMS_KEY_ALIAS=enterprise-production-key

# Monitoring
CLOUDWATCH_LOG_GROUP=/aws/enterprise-dq/production
```

## Local Development

### Using Docker Compose

1. **Start LocalStack**:
   ```bash
   docker-compose up localstack -d
   ```

2. **Start Development Services**:
   ```bash
   docker-compose up app mlflow jupyter -d
   ```

3. **Access Services**:
   - Application: http://localhost:8000
   - MLflow: http://localhost:5000
   - Jupyter: http://localhost:8888

### Using Local Environment

1. **Bootstrap CDK**:
   ```bash
   cdk bootstrap
   ```

2. **Deploy Foundation**:
   ```bash
   cdk deploy enterprise-foundation --require-approval never
   ```

3. **Run Tests**:
   ```bash
   make test
   ```

4. **Generate Test Data**:
   ```bash
   make generate-data
   ```

## Staging Deployment

### 1. Environment Configuration

Set staging environment variables:

```bash
export ENV_NAME=staging
export PROJECT_PREFIX=enterprise
export AWS_REGION=eu-west-2
```

### 2. Deploy Infrastructure

```bash
# Deploy all stacks to staging
make deploy-staging

# Or deploy individual stacks
cdk deploy enterprise-foundation --context env_name=staging
cdk deploy enterprise-data-quality --context env_name=staging
cdk deploy enterprise-document-processing --context env_name=staging
cdk deploy enterprise-ml-inference --context env_name=staging
```

### 3. Verify Deployment

```bash
# Check CloudFormation stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# Check S3 buckets
aws s3 ls | grep enterprise-staging

# Check Lambda functions
aws lambda list-functions --region eu-west-2 | grep enterprise-staging
```

### 4. Run Integration Tests

```bash
# Run integration tests against staging
python -m pytest tests/integration/ -v --env=staging
```

## Production Deployment

### 1. Pre-deployment Checklist

- [ ] All tests passing
- [ ] Security scan completed
- [ ] Performance tests passed
- [ ] Documentation updated
- [ ] Backup strategy in place
- [ ] Rollback plan prepared

### 2. Environment Configuration

Set production environment variables:

```bash
export ENV_NAME=production
export PROJECT_PREFIX=enterprise
export AWS_REGION=eu-west-2
```

### 3. Security Validation

```bash
# Run security scan
make security-scan

# Validate security configuration
python -c "from security.security_config import security_manager; security_manager.validate_encryption_settings()"
```

### 4. Deploy Infrastructure

```bash
# Deploy to production
make deploy-prod

# Or deploy with manual approval
cdk deploy --all --context env_name=production
```

### 5. Post-deployment Verification

```bash
# Verify all services are running
aws cloudwatch describe-alarms --alarm-names enterprise-production-*

# Check application health
curl -f https://your-api-gateway-url/health

# Verify data pipeline
aws glue get-crawlers --region eu-west-2 | grep enterprise-production
```

### 6. Monitoring Setup

```bash
# Set up CloudWatch dashboards
aws cloudwatch put-dashboard --dashboard-name enterprise-production --dashboard-body file://monitoring/dashboards/production.json

# Configure alarms
aws cloudwatch put-metric-alarm --cli-input-json file://monitoring/alarms/production.json
```

## Monitoring and Observability

### CloudWatch Dashboards

Access your CloudWatch dashboards:

1. **Data Quality Dashboard**: Monitor data quality metrics
2. **Pipeline Performance**: Track ETL job performance
3. **Cost Monitoring**: Monitor AWS costs
4. **Security Dashboard**: Track security events

### Log Analysis

```bash
# View application logs
aws logs tail /aws/enterprise-dq/production --follow

# View Lambda function logs
aws logs tail /aws/lambda/enterprise-production-data-quality --follow

# View Glue job logs
aws logs tail /aws-glue/jobs/logs-v2 --follow
```

### Metrics and Alerts

Key metrics to monitor:

- **Data Quality Score**: Should be > 0.85
- **Pipeline Success Rate**: Should be > 95%
- **API Response Time**: Should be < 500ms
- **Error Rate**: Should be < 1%

## Security Configuration

### 1. Encryption Setup

```bash
# Create KMS key
aws kms create-key --description "Enterprise DQ Platform Key" --region eu-west-2

# Create alias
aws kms create-alias --alias-name enterprise-production-key --target-key-id your-key-id
```

### 2. IAM Roles and Policies

```bash
# Create service roles
aws iam create-role --role-name enterprise-production-glue-role --assume-role-policy-document file://iam/glue-trust-policy.json

# Attach policies
aws iam attach-role-policy --role-name enterprise-production-glue-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole
```

### 3. Network Security

```bash
# Create VPC (if not using default)
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Create security groups
aws ec2 create-security-group --group-name enterprise-production-sg --description "Enterprise DQ Platform Security Group"
```

### 4. Compliance Validation

```bash
# Validate GDPR compliance
python -c "from security.security_config import compliance_manager; print(compliance_manager.validate_compliance('GDPR'))"

# Validate SOX compliance
python -c "from security.security_config import compliance_manager; print(compliance_manager.validate_compliance('SOX'))"
```

## Troubleshooting

### Common Issues

#### 1. CDK Deployment Fails

**Error**: `Stack deployment failed`

**Solution**:
```bash
# Check CloudFormation events
aws cloudformation describe-stack-events --stack-name enterprise-foundation

# Check IAM permissions
aws sts get-caller-identity

# Retry deployment
cdk deploy --all --require-approval never
```

#### 2. Lambda Function Errors

**Error**: `Function execution failed`

**Solution**:
```bash
# Check Lambda logs
aws logs tail /aws/lambda/enterprise-production-data-quality --follow

# Check function configuration
aws lambda get-function --function-name enterprise-production-data-quality
```

#### 3. S3 Access Denied

**Error**: `Access Denied to S3 bucket`

**Solution**:
```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket enterprise-raw-production-account-region

# Check IAM permissions
aws iam get-role-policy --role-name enterprise-production-glue-role --policy-name S3Access
```

#### 4. Glue Job Failures

**Error**: `Glue job execution failed`

**Solution**:
```bash
# Check job logs
aws logs tail /aws-glue/jobs/logs-v2 --follow

# Check job configuration
aws glue get-job --job-name enterprise-production-contracts-etl
```

### Performance Optimization

#### 1. Lambda Cold Starts

**Solution**:
- Use provisioned concurrency
- Optimize function size
- Use Lambda layers for dependencies

#### 2. Glue Job Performance

**Solution**:
- Increase worker type
- Optimize Spark configuration
- Use data partitioning

#### 3. S3 Performance

**Solution**:
- Use S3 Transfer Acceleration
- Implement parallel processing
- Use appropriate storage classes

### Support and Maintenance

#### 1. Regular Maintenance

```bash
# Weekly health checks
make health-check

# Monthly cost review
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31 --granularity MONTHLY --metrics BlendedCost

# Quarterly security audit
make security-audit
```

#### 2. Backup and Recovery

```bash
# Create backup
aws s3 sync s3://enterprise-raw-production-account-region s3://enterprise-backup-production-account-region

# Test recovery
aws s3 sync s3://enterprise-backup-production-account-region s3://enterprise-test-recovery-account-region
```

#### 3. Scaling

```bash
# Scale Lambda functions
aws lambda update-function-configuration --function-name enterprise-production-data-quality --timeout 900

# Scale Glue jobs
aws glue update-job --job-name enterprise-production-contracts-etl --job-update WorkerType=G.1X,NumberOfWorkers=10
```

## Conclusion

This deployment guide provides a comprehensive approach to deploying the Enterprise Data Quality & Compliance Platform. Follow the steps carefully and ensure all prerequisites are met before proceeding with deployment.

For additional support:

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/enterprise-data-quality-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/enterprise-data-quality-platform/discussions)
- **Enterprise Support**: enterprise-support@company.com
