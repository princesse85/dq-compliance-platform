# Enterprise Data Quality & Compliance Platform - Quick Deploy Script
# This script provides a simple way to deploy the platform on Windows

param(
    [string]$Action = "deploy"
)

Write-Host "🚀 Enterprise Data Quality & Compliance Platform - Quick Deploy" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to validate AWS credentials
function Test-AwsCredentials {
    Write-Host "🔍 Validating AWS credentials..." -ForegroundColor Blue
    
    try {
        $identity = aws sts get-caller-identity 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "AWS credentials not configured"
        }
        
        $accountId = aws sts get-caller-identity --query Account --output text 2>$null
        $region = aws configure get region 2>$null
        if (-not $region) {
            Write-Host "❌ AWS region not configured. Please run 'aws configure' first." -ForegroundColor Red
            exit 1
        }
        
        Write-Host "✅ AWS credentials validated successfully" -ForegroundColor Green
        Write-Host "   Account ID: $accountId" -ForegroundColor White
        Write-Host "   Region: $region" -ForegroundColor White
        
        return @{
            AccountId = $accountId
            Region = $region
        }
    }
    catch {
        Write-Host "❌ AWS credentials are not configured or invalid" -ForegroundColor Red
        Write-Host "Please configure your AWS credentials first:" -ForegroundColor Yellow
        Write-Host "  1. Run: aws configure" -ForegroundColor White
        Write-Host "  2. Enter your AWS Access Key ID" -ForegroundColor White
        Write-Host "  3. Enter your AWS Secret Access Key" -ForegroundColor White
        Write-Host "  4. Enter your default region (e.g., us-east-1)" -ForegroundColor White
        Write-Host "  5. Enter your output format (json)" -ForegroundColor White
        exit 1
    }
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Blue
    
    $missingDeps = @()
    
    # Check Python
    if (-not (Test-Command "python")) {
        $missingDeps += "python"
    }
    
    # Check pip
    if (-not (Test-Command "pip")) {
        $missingDeps += "pip"
    }
    
    # Check AWS CLI
    if (-not (Test-Command "aws")) {
        $missingDeps += "aws-cli"
    }
    
    # Check Node.js (for CDK)
    if (-not (Test-Command "node")) {
        $missingDeps += "nodejs"
    }
    
    # Check npm
    if (-not (Test-Command "npm")) {
        $missingDeps += "npm"
    }
    
    if ($missingDeps.Count -gt 0) {
        Write-Host "❌ Missing required dependencies: $($missingDeps -join ', ')" -ForegroundColor Red
        Write-Host "Please install the missing dependencies:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Windows:" -ForegroundColor White
        Write-Host "  Download and install from:" -ForegroundColor White
        Write-Host "  - Python: https://www.python.org/downloads/" -ForegroundColor White
        Write-Host "  - Node.js: https://nodejs.org/" -ForegroundColor White
        Write-Host "  - AWS CLI: https://aws.amazon.com/cli/" -ForegroundColor White
        Write-Host ""
        Write-Host "Or use Chocolatey:" -ForegroundColor White
        Write-Host "  choco install python nodejs awscli" -ForegroundColor White
        exit 1
    }
    
    Write-Host "✅ All prerequisites are installed" -ForegroundColor Green
}

# Function to setup environment
function Setup-Environment {
    Write-Host "🔧 Setting up environment..." -ForegroundColor Blue
    
    # Create virtual environment if it doesn't exist
    if (-not (Test-Path ".venv")) {
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        python -m venv .venv
    }
    
    # Activate virtual environment
    & ".venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install dependencies
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    # Install CDK if not already installed
    if (-not (Test-Command "cdk")) {
        Write-Host "Installing AWS CDK..." -ForegroundColor Yellow
        npm install -g aws-cdk
    }
    
    Write-Host "✅ Environment setup completed" -ForegroundColor Green
}

# Function to bootstrap CDK
function Start-CdkBootstrap {
    Write-Host "🚀 Bootstrapping AWS CDK..." -ForegroundColor Blue
    
    # Activate virtual environment
    & ".venv\Scripts\Activate.ps1"
    
    # Bootstrap CDK
    cdk bootstrap
    
    Write-Host "✅ CDK bootstrapped successfully" -ForegroundColor Green
}

# Function to deploy stacks
function Start-Deploy {
    Write-Host "🚀 Deploying infrastructure stacks..." -ForegroundColor Blue
    
    # Activate virtual environment
    & ".venv\Scripts\Activate.ps1"
    
    # Deploy all stacks
    cdk deploy --all --require-approval never
    
    Write-Host "✅ All stacks deployed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 Your Enterprise Data Quality & Compliance Platform is now live!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Check the CDK outputs above for your API endpoints" -ForegroundColor White
    Write-Host "  2. Test your deployment with: .\scripts\deploy.ps1 test" -ForegroundColor White
    Write-Host "  3. Monitor your resources in the AWS Console" -ForegroundColor White
}

# Function to run tests
function Start-Tests {
    Write-Host "🧪 Running tests..." -ForegroundColor Blue
    
    # Activate virtual environment
    & ".venv\Scripts\Activate.ps1"
    
    # Run tests
    python -m pytest tests/ -v
    
    Write-Host "✅ Tests completed successfully" -ForegroundColor Green
}

# Function to show usage
function Show-Usage {
    Write-Host "Enterprise Data Quality & Compliance Platform - Quick Deploy" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 [OPTION]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor White
    Write-Host "  deploy         Deploy all infrastructure stacks (default)" -ForegroundColor White
    Write-Host "  setup          Setup environment and bootstrap CDK" -ForegroundColor White
    Write-Host "  test           Run tests" -ForegroundColor White
    Write-Host "  validate       Validate AWS credentials" -ForegroundColor White
    Write-Host "  help           Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "  .\deploy.ps1 deploy      # Deploy infrastructure" -ForegroundColor White
    Write-Host "  .\deploy.ps1 setup       # Setup environment" -ForegroundColor White
    Write-Host "  .\deploy.ps1 test        # Run tests" -ForegroundColor White
}

# Main script logic
switch ($Action.ToLower()) {
    "deploy" {
        Test-Prerequisites
        Test-AwsCredentials | Out-Null
        Setup-Environment
        Start-CdkBootstrap
        Start-Deploy
    }
    "setup" {
        Test-Prerequisites
        Test-AwsCredentials | Out-Null
        Setup-Environment
        Start-CdkBootstrap
        Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
        Write-Host "Run: .\deploy.ps1 deploy" -ForegroundColor Yellow
    }
    "test" {
        Setup-Environment
        Start-Tests
    }
    "validate" {
        Test-AwsCredentials | Out-Null
    }
    "help" {
        Show-Usage
    }
    default {
        Write-Host "❌ Unknown option: $Action" -ForegroundColor Red
        Show-Usage
        exit 1
    }
}
