#!/bin/bash

# Legal Compliance Platform - Phase 4 Lambda Container Build & Deploy
# This script builds the Lambda container image and deploys it to ECR

set -e

# Configuration
PROJECT_PREFIX=${PROJECT_PREFIX:-"legal"}
ENV_NAME=${ENV_NAME:-"dev2"}
AWS_REGION=${AWS_REGION:-"us-east-1"}
ECR_REPO_NAME="${PROJECT_PREFIX}-${ENV_NAME}-legal-infer-repo"
IMAGE_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check if AWS CLI is configured
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        log_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "Dockerfile" ]; then
        log_error "Dockerfile not found. Please run this script from the lambda_app directory."
        exit 1
    fi
    
    log_info "Prerequisites check passed."
}

# Get AWS account ID
get_account_id() {
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo $ACCOUNT_ID
}

# Create ECR repository if it doesn't exist
create_ecr_repo() {
    log_info "Checking if ECR repository exists..."
    
    if aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION > /dev/null 2>&1; then
        log_info "ECR repository $ECR_REPO_NAME already exists."
    else
        log_info "Creating ECR repository $ECR_REPO_NAME..."
        aws ecr create-repository \
            --repository-name $ECR_REPO_NAME \
            --region $AWS_REGION \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256
    fi
}

# Get ECR login token
get_ecr_login() {
    log_info "Getting ECR login token..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."
    
    # Create models directory if it doesn't exist
    mkdir -p models/baseline models/transformer
    
    # Create dummy model files if they don't exist (for testing)
    if [ ! -f "models/baseline/model.joblib" ]; then
        log_warn "No baseline model found. Creating dummy model for testing..."
        python -c "
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import os

# Create dummy pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
    ('classifier', LogisticRegression(random_state=42))
])

# Train on dummy data
dummy_texts = [
    'This is a low risk contract with standard terms.',
    'This is a high risk contract with indemnification clauses.',
    'Standard service agreement with normal liability limits.',
    'Contract includes unlimited liability and indemnification.'
]
dummy_labels = ['LowRisk', 'HighRisk', 'LowRisk', 'HighRisk']

pipeline.fit(dummy_texts, dummy_labels)

# Save the model
os.makedirs('models/baseline', exist_ok=True)
joblib.dump(pipeline, 'models/baseline/model.joblib')
print('Dummy baseline model created.')
"
    fi
    
    # Build the image
    docker build -t $ECR_REPO_NAME:$IMAGE_TAG .
    
    log_info "Docker image built successfully."
}

# Tag and push image to ECR
push_image() {
    log_info "Tagging and pushing image to ECR..."
    
    ECR_URI=$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME
    
    # Tag the image
    docker tag $ECR_REPO_NAME:$IMAGE_TAG $ECR_URI:$IMAGE_TAG
    
    # Push the image
    docker push $ECR_URI:$IMAGE_TAG
    
    log_info "Image pushed successfully to ECR."
    echo "ECR Image URI: $ECR_URI:$IMAGE_TAG"
}

# Update Lambda function
update_lambda() {
    log_info "Updating Lambda function..."
    
    FUNCTION_NAME="${PROJECT_PREFIX}-${ENV_NAME}-legal-infer"
    ECR_URI=$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$IMAGE_TAG
    
    # Check if function exists
    if aws lambda get-function --function-name $FUNCTION_NAME --region $AWS_REGION > /dev/null 2>&1; then
        log_info "Updating existing Lambda function..."
        aws lambda update-function-code \
            --function-name $FUNCTION_NAME \
            --image-uri $ECR_URI \
            --region $AWS_REGION
        
        # Wait for update to complete
        log_info "Waiting for Lambda function update to complete..."
        aws lambda wait function-updated --function-name $FUNCTION_NAME --region $AWS_REGION
        
        log_info "Lambda function updated successfully."
    else
        log_warn "Lambda function $FUNCTION_NAME does not exist. Please deploy the CDK stack first."
        log_info "You can deploy the CDK stack with: cdk deploy"
    fi
}

# Create Lambda versions for A/B testing
create_versions() {
    log_info "Creating Lambda versions for A/B testing..."
    
    FUNCTION_NAME="${PROJECT_PREFIX}-${ENV_NAME}-legal-infer"
    
    # Check if function exists
    if ! aws lambda get-function --function-name $FUNCTION_NAME --region $AWS_REGION > /dev/null 2>&1; then
        log_warn "Lambda function $FUNCTION_NAME does not exist. Skipping version creation."
        return
    fi
    
    # Create Version A (Baseline)
    log_info "Creating Version A (Baseline)..."
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --environment Variables='{MODEL_VARIANT=baseline}' \
        --region $AWS_REGION
    
    aws lambda wait function-updated --function-name $FUNCTION_NAME --region $AWS_REGION
    
    VERSION_A=$(aws lambda publish-version \
        --function-name $FUNCTION_NAME \
        --description "Baseline model version" \
        --region $AWS_REGION \
        --query Version \
        --output text)
    
    log_info "Version A (Baseline) created: $VERSION_A"
    
    # Create Version B (Transformer)
    log_info "Creating Version B (Transformer)..."
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --environment Variables='{MODEL_VARIANT=transformer}' \
        --region $AWS_REGION
    
    aws lambda wait function-updated --function-name $FUNCTION_NAME --region $AWS_REGION
    
    VERSION_B=$(aws lambda publish-version \
        --function-name $FUNCTION_NAME \
        --description "Transformer model version" \
        --region $AWS_REGION \
        --query Version \
        --output text)
    
    log_info "Version B (Transformer) created: $VERSION_B"
    
    # Create alias with routing
    log_info "Creating alias with A/B routing..."
    ALIAS_NAME="prod"
    
    # Check if alias exists
    if aws lambda get-alias --function-name $FUNCTION_NAME --name $ALIAS_NAME --region $AWS_REGION > /dev/null 2>&1; then
        log_info "Updating existing alias..."
        aws lambda update-alias \
            --function-name $FUNCTION_NAME \
            --name $ALIAS_NAME \
            --function-version $VERSION_A \
            --routing-config AdditionalVersionWeights="{\"$VERSION_B\":0.1}" \
            --region $AWS_REGION
    else
        log_info "Creating new alias..."
        aws lambda create-alias \
            --function-name $FUNCTION_NAME \
            --name $ALIAS_NAME \
            --function-version $VERSION_A \
            --routing-config AdditionalVersionWeights="{\"$VERSION_B\":0.1}" \
            --region $AWS_REGION
    fi
    
    log_info "A/B testing setup complete!"
    log_info "Version A (Baseline): $VERSION_A (90% traffic)"
    log_info "Version B (Transformer): $VERSION_B (10% traffic)"
}

# Main execution
main() {
    log_info "Starting Lambda container build and deploy process..."
    
    # Get AWS account ID
    ACCOUNT_ID=$(get_account_id)
    log_info "AWS Account ID: $ACCOUNT_ID"
    
    # Run all steps
    check_prerequisites
    create_ecr_repo
    get_ecr_login
    build_image
    push_image
    update_lambda
    create_versions
    
    log_info "Build and deploy process completed successfully!"
    
    # Display summary
    echo ""
    echo "=== DEPLOYMENT SUMMARY ==="
    echo "ECR Repository: $ECR_REPO_NAME"
    echo "Image URI: $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$IMAGE_TAG"
    echo "Lambda Function: ${PROJECT_PREFIX}-${ENV_NAME}-legal-infer"
    echo "Alias: prod (with A/B routing)"
    echo "Region: $AWS_REGION"
    echo ""
    echo "Next steps:"
    echo "1. Test the API endpoint"
    echo "2. Monitor CloudWatch logs"
    echo "3. Adjust A/B routing weights as needed"
}

# Run main function
main "$@"
