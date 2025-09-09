# This script deploys the DQ Compliance Platform to a specified environment.
# Usage: ./deploy.ps1 -EnvironmentName [staging|production] [-SkipImagePush]

param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("staging", "production")]
    [string]$EnvironmentName,
    [switch]$SkipImagePush
)

# Build and push the Docker image if not skipped
if (-not $SkipImagePush) {
    Write-Host "Building and pushing the Docker image..."
    powershell.exe -File build_and_push_ecr_image.ps1 -AwsRegion "eu-west-2" -RepositoryName "dq-platform-$EnvironmentName-ml-inference-repo" -ImageTag "latest"
}

# Deploy the UnifiedStack to the specified environment
Write-Host "Deploying the DQ Compliance Platform to the $EnvironmentName environment..."
cdk deploy --context env_name=$EnvironmentName --all --require-approval never