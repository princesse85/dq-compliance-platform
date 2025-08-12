# Simple ML Inference Platform - Deployment Guide

## 🚀 Overview

A simplified, production-ready ML inference API with A/B testing capabilities. This guide covers the essential deployment steps.

## 🏗️ Architecture

### Core Components

- **API Gateway**: RESTful API for ML inference
- **Lambda Container**: Serverless inference with containerized ML models
- **ECR Repository**: Container registry for Lambda images
- **CloudWatch**: Basic monitoring and alerting
- **SNS**: Simple alert notifications

## 📋 Prerequisites

### Required Tools

```bash
aws-cli/2.15.0+          # AWS CLI v2
docker/24.0.0+           # Docker Desktop
cdk/2.100.0+             # AWS CDK CLI
python/3.11+             # Python runtime
```

### AWS Permissions

- `CloudFormation:*` (for CDK deployment)
- `IAM:*` (roles and policies)
- `Lambda:*` (function management)
- `ECR:*` (container registry)
- `API Gateway:*` (API management)
- `CloudWatch:*` (monitoring)
- `SNS:*` (notifications)

## 🔧 Configuration

### Environment Variables

```bash
export PROJECT_PREFIX="enterprise"
export ENV_NAME="production"
export AWS_REGION="eu-west-2"
export CDK_DEFAULT_ACCOUNT="123456789012"
export CDK_DEFAULT_REGION="eu-west-2"
```

## 🚀 Deployment Steps

### Step 1: Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd dq-compliance-platform

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap
```

### Step 2: Deploy Foundation Infrastructure

```bash
# Deploy foundation stack
cdk deploy enterprise-foundation --require-approval never

# Verify deployment
aws cloudformation describe-stacks --stack-name enterprise-production-foundation
```

### Step 3: Deploy ML Inference Infrastructure

```bash
# Deploy ML inference stack
cdk deploy enterprise-ml-inference --require-approval never

# Verify resources
aws lambda list-functions --query "Functions[?contains(FunctionName, 'enterprise-production-ml-inference')]"
aws apigateway get-rest-apis --query "items[?name=='enterprise-production-ml-inference-api']"
```

### Step 4: Build and Deploy Lambda Container

```bash
# Navigate to lambda app directory
cd lambda_app

# Make build script executable
chmod +x build_and_deploy.sh

# Run build and deploy
./build_and_deploy.sh

# Verify deployment
aws lambda get-function --function-name enterprise-production-ml-inference
```

### Step 5: Configure A/B Testing

```bash
# Create Lambda versions for A/B testing
aws lambda publish-version --function-name enterprise-production-ml-inference --description "Baseline model v1"

# Create alias with weighted routing
aws lambda create-alias \
  --function-name enterprise-production-ml-inference \
  --name prod \
  --function-version 1 \
  --routing-config AdditionalVersionWeights='{"2":0.1}'

# Verify alias
aws lambda get-alias --function-name enterprise-production-ml-inference --name prod
```

## 🧪 Testing

### API Testing

```bash
# Get API endpoint
API_ENDPOINT=$(aws ssm get-parameter --name "/enterprise/production/ml-inference/api-endpoint" --query Parameter.Value --output text)

# Test health endpoint
curl -X GET "${API_ENDPOINT}/health"

# Test models endpoint
curl -X GET "${API_ENDPOINT}/models"

# Test prediction endpoint
curl -X POST "${API_ENDPOINT}/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contract includes indemnification clauses.",
    "model": "baseline",
    "explain": true
  }'
```

## 📊 Monitoring

### CloudWatch Alarms

The platform automatically creates:

- **Error Rate**: >5 errors in 5 minutes
- **Duration**: >25 seconds average duration

### Log Analysis

```bash
# View Lambda logs
aws logs tail /aws/lambda/enterprise-production-ml-inference --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/enterprise-production-ml-inference \
  --filter-pattern "ERROR"
```

## 🔄 A/B Testing Management

### Traffic Distribution

```bash
# Current distribution (90% baseline, 10% transformer)
aws lambda get-alias --function-name enterprise-production-ml-inference --name prod

# Update to 50/50 split
aws lambda update-alias \
  --function-name enterprise-production-ml-inference \
  --name prod \
  --routing-config AdditionalVersionWeights='{"2":0.5}'

# Update to 100% transformer
aws lambda update-alias \
  --function-name enterprise-production-ml-inference \
  --name prod \
  --routing-config AdditionalVersionWeights='{"2":1.0}'
```

## 🛠️ Maintenance

### Regular Tasks

```bash
# Daily
- Monitor CloudWatch alarms
- Check error rates

# Weekly
- Review Lambda function performance
- Analyze A/B testing results

# Monthly
- Update dependencies
- Optimize costs
```

### Updates

```bash
# Update Lambda function code
aws lambda update-function-code \
  --function-name enterprise-production-ml-inference \
  --image-uri <new-image-uri>

# Update API Gateway
cdk deploy enterprise-ml-inference --require-approval never
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Lambda Errors

```bash
# Check error logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/enterprise-production-ml-inference \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000
```

#### 2. API Gateway Issues

```bash
# Check API Gateway logs
aws logs filter-log-events \
  --log-group-name /aws/apigateway/enterprise-production-ml-inference \
  --filter-pattern "ERROR"
```

#### 3. Model Loading Issues

```bash
# Check model loading logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/enterprise-production-ml-inference \
  --filter-pattern "Failed to load"
```

## 🎯 Success Metrics

### Performance Targets

- **Latency**: < 30 seconds
- **Error Rate**: < 5%
- **Availability**: 99%

### Business Metrics

- **A/B Testing Results**: Model performance comparison
- **Cost Optimization**: Efficient resource utilization

## 📞 Support

### Getting Help

- **Documentation**: Check this guide
- **Logs**: Review CloudWatch logs
- **AWS Support**: Contact AWS support for infrastructure issues

---

## 🎉 Conclusion

This simplified deployment guide provides essential instructions for deploying and maintaining the ML Inference Platform. The platform is designed to be:

- **Simple**: Minimal complexity with essential features
- **Scalable**: Automatic scaling with Lambda
- **Observable**: Basic monitoring and alerting
- **Maintainable**: Infrastructure as code with CDK
- **Cost-effective**: Pay-per-use with budget controls
