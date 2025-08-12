# Enterprise Data Quality & Compliance Platform - Setup Script (PowerShell)
# This script helps users set up their environment and deploy the platform

param(
    [Parameter(Position=0)]
    [string]$Action = "setup"
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

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
    Write-Status "Validating AWS credentials..."
    
    try {
        $identity = aws sts get-caller-identity 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "AWS credentials not configured"
        }
        
        $accountId = aws sts get-caller-identity --query Account --output text 2>$null
        $region = aws configure get region 2>$null
        
        Write-Success "AWS credentials validated successfully"
        Write-Status "Account ID: $accountId"
        Write-Status "Region: $region"
        
        return @{
            AccountId = $accountId
            Region = $region
        }
    }
    catch {
        Write-Error "AWS credentials are not configured or invalid"
        Write-Status "Please configure your AWS credentials first:"
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
    Write-Status "Checking prerequisites..."
    
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
    
    # Check Docker (optional)
    if (-not (Test-Command "docker")) {
        Write-Warning "Docker not found. Local development with Docker Compose will not be available."
    }
    
    if ($missingDeps.Count -gt 0) {
        Write-Error "Missing required dependencies: $($missingDeps -join ', ')"
        Write-Status "Please install the missing dependencies:"
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
    
    Write-Success "All prerequisites are installed"
}

# Function to install Python dependencies
function Install-Dependencies {
    Write-Status "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if (-not (Test-Path ".venv")) {
        Write-Status "Creating virtual environment..."
        python -m venv .venv
    }
    
    # Activate virtual environment
    & ".venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements.txt
    
    Write-Success "Python dependencies installed successfully"
}

# Function to install CDK
function Install-CDK {
    Write-Status "Installing AWS CDK..."
    
    # Check if CDK is already installed
    if (-not (Test-Command "cdk")) {
        npm install -g aws-cdk
        Write-Success "AWS CDK installed successfully"
    }
    else {
        Write-Status "AWS CDK is already installed"
    }
}

# Function to configure environment
function Set-Environment {
    param($AwsInfo)
    
    Write-Status "Configuring environment..."
    
    # Use the Python configuration script
    python scripts/configure_env.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Environment configuration failed"
        exit 1
    }
    
    Write-Success "Environment configuration completed"
}

# Function to bootstrap CDK
function Start-CdkBootstrap {
    Write-Status "Bootstrapping AWS CDK..."
    
    # Activate virtual environment
    & ".venv\Scripts\Activate.ps1"
    
    # Bootstrap CDK
    cdk bootstrap
    
    Write-Success "CDK bootstrapped successfully"
}

# Function to deploy stacks
function Start-Deploy {
    Write-Status "Deploying infrastructure stacks..."
    
    # Activate virtual environment
    & ".venv\Scripts\Activate.ps1"
    
    # Deploy all stacks
    cdk deploy --all --require-approval never
    
    Write-Success "All stacks deployed successfully"
}

# Function to run tests
function Start-Tests {
    Write-Status "Running tests..."
    
    # Activate virtual environment
    & ".venv\Scripts\Activate.ps1"
    
    # Run tests
    python -m pytest tests/ -v
    
    Write-Success "Tests completed successfully"
}

# Function to show usage
function Show-Usage {
    Write-Host "Enterprise Data Quality & Compliance Platform - Setup Script" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\setup.ps1 [OPTION]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor White
    Write-Host "  setup          Complete setup (prerequisites, dependencies, configuration)" -ForegroundColor White
    Write-Host "  deploy         Deploy all infrastructure stacks" -ForegroundColor White
    Write-Host "  test           Run tests" -ForegroundColor White
    Write-Host "  bootstrap      Bootstrap CDK" -ForegroundColor White
    Write-Host "  validate       Validate AWS credentials" -ForegroundColor White
    Write-Host "  help           Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "  .\setup.ps1 setup       # Complete setup" -ForegroundColor White
    Write-Host "  .\setup.ps1 deploy      # Deploy infrastructure" -ForegroundColor White
    Write-Host "  .\setup.ps1 test        # Run tests" -ForegroundColor White
}

# Main script logic
switch ($Action.ToLower()) {
    "setup" {
        Write-Status "Starting complete setup..."
        Test-Prerequisites
        $awsInfo = Test-AwsCredentials
        Install-Dependencies
        Install-CDK
        Set-Environment -AwsInfo $awsInfo
        Start-CdkBootstrap
        Write-Success "Setup completed successfully!"
        Write-Status "Next steps:"
        Write-Host "  1. Update .env with your security settings" -ForegroundColor White
        Write-Host "  2. Run: .\setup.ps1 deploy" -ForegroundColor White
        Write-Host "  3. Run: .\setup.ps1 test" -ForegroundColor White
    }
    "deploy" {
        Test-AwsCredentials | Out-Null
        Install-Dependencies
        Start-Deploy
    }
    "test" {
        Install-Dependencies
        Start-Tests
    }
    "bootstrap" {
        Test-AwsCredentials | Out-Null
        Install-Dependencies
        Start-CdkBootstrap
    }
    "validate" {
        Test-AwsCredentials | Out-Null
    }
    "help" {
        Show-Usage
    }
    default {
        Write-Error "Unknown option: $Action"
        Show-Usage
        exit 1
    }
}
