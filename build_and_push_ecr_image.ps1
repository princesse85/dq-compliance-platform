
# This script builds and pushes a Docker image to an ECR repository.
# Usage: ./build_and_push_ecr_image.ps1 -AwsRegion [aws_region] -RepositoryName [repository_name] -ImageTag [image_tag]

param (
    [Parameter(Mandatory=$true)]
    [string]$AwsRegion,
    [Parameter(Mandatory=$true)]
    [string]$RepositoryName,
    [Parameter(Mandatory=$true)]
    [string]$ImageTag
)

# Get the AWS account ID
$AwsAccountId = (aws sts get-caller-identity --query "Account" --output text)

# Log in to ECR
aws ecr get-login-password --region $AwsRegion | docker login --username AWS --password-stdin "$AwsAccountId.dkr.ecr.$AwsRegion.amazonaws.com"

# Build the Docker image
docker build -t "$RepositoryName`:$ImageTag" "lambda_app"

# Tag the image
docker tag "$RepositoryName`:$ImageTag" "$AwsAccountId.dkr.ecr.$AwsRegion.amazonaws.com/$RepositoryName`:$ImageTag"

# Push the image to ECR
docker push "$AwsAccountId.dkr.ecr.$AwsRegion.amazonaws.com/$RepositoryName`:$ImageTag"
