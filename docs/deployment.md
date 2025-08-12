# Enterprise Data Quality Platform - Deployment Guide

## Overview

This guide covers the deployment of the Enterprise Data Quality Platform, which includes:

- **Foundation Infrastructure** (Phase 0): S3 buckets, IAM roles, CloudTrail, billing alarms
- **Data Quality Pipeline** (Phase 1): Glue jobs, data validation, quality monitoring
- **ML Inference API** (Phase 4): Lambda container with A/B testing for model comparison

## Prerequisites

### Required Tools

- AWS CLI v2+ configured with appropriate permissions
- Docker Desktop running
- CDK CLI installed (`npm install -g aws-cdk`)
- Python 3.11+ with virtual environment
- Git

### AWS Permissions

Ensure your AWS credentials have permissions for:

- CloudFormation (for CDK)
- IAM (roles and policies)
- S3 (buckets and objects)
- Lambda (functions and containers)
- ECR (container registry)
- API Gateway
- CloudWatch (logs and metrics)
- SSM (parameter store)

## Configuration

### Environment Variables

The platform uses the following configuration (from `cdk.json`):

```json
{
  "project_prefix": "enterprise",
  "env_name": "production",
  "region": "eu-west-2",
  "billing_email": "enterprise-support@company.com",
  "monthly_budget": 5000
}
```

### Customization

You can override these settings by:

1. **Modifying cdk.json** directly
2. **Using CDK context**: `cdk deploy --context project_prefix=mycompany --context env_name=dev`
3. **Environment variables**: `export CDK_DEFAULT_REGION=us-east-1`

## Deployment Steps

### Step 1: Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd dq-compliance-platform

# Create and activate virtual environment
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
cdk deploy enterprise-foundation

# This creates:
# - S3 buckets (raw, processed, analytics, audit)
# - IAM roles and policies
# - CloudTrail for audit logging
# - SNS topic for alerts
# - AWS Budget with $5000 monthly limit
```

### Step 3: Deploy Billing Alarms

```bash
# Deploy billing alarms (us-east-1 required)
cdk deploy enterprise-billing

# This creates:
# - CloudWatch alarms for budget monitoring
# - SNS notifications for cost alerts
```

### Step 4: Deploy Data Quality Pipeline

```bash
# Deploy data quality stack
cdk deploy enterprise-data-quality

# This creates:
# - Glue jobs for data processing
# - Data quality validation rules
# - Monitoring dashboards
```

### Step 5: Deploy ML Inference API

```bash
# Deploy ML inference stack
cdk deploy enterprise-ml-inference

# This creates:
# - ECR repository for Lambda container
# - Lambda function with container image
# - API Gateway with /predict endpoint
# - IAM roles and policies
# - SSM parameters for configuration
```

### Step 6: Build and Deploy Lambda Container

```bash
# Navigate to lambda application directory
cd lambda_app

# Make build script executable (Linux/Mac)
chmod +x build_and_deploy.sh

# Run build and deploy script
./build_and_deploy.sh
```

The build script will:

- Create dummy models for testing (if Phase 3 models not available)
- Build Docker container image
- Push to ECR
- Update Lambda function
- Create Lambda versions for A/B testing
- Set up alias with 90/10 routing (baseline/transformer)

### Step 7: Test the API

```bash
# Get the API endpoint URL
aws ssm get-parameter --name "/enterprise/production/api-endpoint" --query Parameter.Value --output text

# Test the API
python test_api.py https://your-api-id.execute-api.eu-west-2.amazonaws.com/prod
```

## API Usage

### Endpoints

- **Health Check**: `GET /health`
- **Models Status**: `GET /models`
- **Prediction**: `POST /predict`

### Request Format

```json
{
  "text": "Contract includes indemnification clauses.",
  "model": "auto|baseline|transformer",
  "explain": true,
  "doc_id": "optional-document-id"
}
```

### Response Format

```json
{
  "model": "baseline",
  "label": "HighRisk",
  "confidence": 0.87,
  "explanation": {
    "type": "tokens",
    "top_terms": ["indemnify", "liability"],
    "html_url": null
  },
  "timings_ms": { "pre": 3, "infer": 40, "post": 2 }
}
```

### Example Usage

```bash
# Basic prediction
curl -X POST "https://your-api.execute-api.eu-west-2.amazonaws.com/prod/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Standard service agreement with normal terms.",
    "model": "baseline",
    "explain": true
  }'

# Transformer with pre-computed explanation
curl -X POST "https://your-api.execute-api.eu-west-2.amazonaws.com/prod/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contract includes comprehensive indemnification.",
    "doc_id": "contract_001",
    "model": "transformer",
    "explain": true
  }'
```

## A/B Testing Configuration

### Current Setup

- **Version A (Baseline)**: 90% of traffic
- **Version B (Transformer)**: 10% of traffic

### Adjusting Traffic Split

```bash
# Update traffic distribution
aws lambda update-alias \
  --function-name enterprise-production-ml-infer \
  --name prod \
  --routing-config AdditionalVersionWeights='{"2":0.5,"3":0.5}' \
  --region eu-west-2
```

### Monitoring A/B Performance

```bash
# View CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=enterprise-production-ml-infer \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

## Monitoring and Troubleshooting

### CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/enterprise-production-ml-infer --follow

# View API Gateway logs
aws logs describe-log-groups --log-group-name-prefix "API-Gateway-Execution-Logs"
```

### Health Checks

```bash
# API health
curl https://your-api.execute-api.eu-west-2.amazonaws.com/prod/health

# Models status
curl https://your-api.execute-api.eu-west-2.amazonaws.com/prod/models
```

### Common Issues

1. **Model Loading Failures**

   - Check if model files exist in S3
   - Verify Lambda has S3 read permissions
   - Check CloudWatch logs for specific errors

2. **Timeout Errors**

   - Increase Lambda timeout (max 15 minutes)
   - Optimize model size or use smaller models
   - Consider provisioned concurrency for production

3. **Memory Errors**

   - Increase Lambda memory allocation
   - Optimize model loading
   - Use model quantization

4. **Cold Start Delays**
   - Consider provisioned concurrency
   - Use smaller, optimized models
   - Implement warm-up mechanisms

## Cost Optimization

### Budget Guardrails

- **Monthly Budget**: $5000 with 80% alert threshold
- **Lambda Reserved Concurrency**: 2 (hard cap)
- **Timeout**: 30 seconds (prevents runaway costs)
- **No Persistent Endpoints**: Lambda only

### Cost Monitoring

```bash
# Check Lambda costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-02 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["AWS Lambda"]}}'
```

### Optimization Tips

- Use Lambda container images for consistent deployments
- Implement proper error handling to avoid retries
- Monitor and adjust reserved concurrency based on usage
- Use CloudWatch alarms for cost monitoring

## Security

### IAM Permissions

- Lambda has read-only access to S3 analytics bucket
- API Gateway logs to CloudWatch
- No public access to S3 (pre-signed URLs only)

### Data Protection

- Text content not logged (only hashes/IDs)
- KMS encryption on S3 buckets
- HTTPS-only API access
- VPC isolation (if required)

### Compliance

- CloudTrail for audit logging
- S3 versioning for data retention
- Encrypted storage and transmission
- Access logging enabled

## Scaling and Performance

### Performance Targets

- **Latency**: p95 < 5 seconds
- **Error Rate**: < 1%
- **Throughput**: Configurable based on concurrency limits
- **Cost per Request**: < $0.001

### Scaling Considerations

- **Lambda Concurrency**: Adjust based on expected load
- **API Gateway**: Automatic scaling
- **S3**: No scaling limits for read operations
- **CloudWatch**: Automatic scaling for logs

### Production Recommendations

- Use provisioned concurrency for consistent performance
- Implement proper monitoring and alerting
- Set up automated backups and disaster recovery
- Consider multi-region deployment for global users

## Maintenance

### Regular Tasks

- Monitor CloudWatch metrics and logs
- Review and update IAM permissions
- Check for security updates
- Monitor costs and optimize usage
- Update models and retrain as needed

### Backup and Recovery

- S3 buckets have versioning enabled
- CloudFormation templates for infrastructure
- Lambda function versions for rollback
- SSM parameters for configuration

### Updates and Upgrades

- Update dependencies regularly
- Test new model versions before deployment
- Use blue-green deployment for zero-downtime updates
- Maintain backward compatibility

## Support and Troubleshooting

### Getting Help

- Check CloudWatch logs for detailed error messages
- Review API Gateway access logs
- Monitor Lambda function metrics
- Use AWS X-Ray for distributed tracing

### Common Commands

```bash
# List all stacks
cdk list

# View stack details
cdk diff enterprise-ml-inference

# Destroy specific stack
cdk destroy enterprise-ml-inference

# Update Lambda function code
aws lambda update-function-code --function-name enterprise-production-ml-infer --image-uri <new-image-uri>

# View Lambda function configuration
aws lambda get-function --function-name enterprise-production-ml-infer
```

### Emergency Procedures

- **Service Outage**: Check CloudWatch alarms and logs
- **Cost Spike**: Review Lambda metrics and S3 access
- **Security Incident**: Review CloudTrail logs
- **Data Loss**: Check S3 versioning and backups

## Conclusion

This deployment guide covers the complete setup of the Enterprise Data Quality Platform. The system is designed to be:

- **Cost-effective**: Pay-per-use with budget controls
- **Scalable**: Automatic scaling with Lambda and API Gateway
- **Secure**: IAM controls, encryption, and audit logging
- **Maintainable**: Infrastructure as code with CDK
- **Observable**: Comprehensive monitoring and logging

For additional support or questions, refer to the AWS documentation or contact the platform team.
