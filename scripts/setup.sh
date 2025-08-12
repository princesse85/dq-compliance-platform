#!/bin/bash

# Enterprise Data Quality & Compliance Platform - Setup Script
# This script helps users set up their environment and deploy the platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate AWS credentials
validate_aws_credentials() {
    print_status "Validating AWS credentials..."
    
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS credentials are not configured or invalid"
        print_status "Please configure your AWS credentials first:"
        echo "  1. Run: aws configure"
        echo "  2. Enter your AWS Access Key ID"
        echo "  3. Enter your AWS Secret Access Key"
        echo "  4. Enter your default region (e.g., us-east-1)"
        echo "  5. Enter your output format (json)"
        exit 1
    fi
    
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region)
    
    print_success "AWS credentials validated successfully"
    print_status "Account ID: $AWS_ACCOUNT_ID"
    print_status "Region: $AWS_REGION"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_deps=()
    
    # Check Python
    if ! command_exists python3; then
        missing_deps+=("python3")
    fi
    
    # Check pip
    if ! command_exists pip3; then
        missing_deps+=("pip3")
    fi
    
    # Check AWS CLI
    if ! command_exists aws; then
        missing_deps+=("aws-cli")
    fi
    
    # Check Node.js (for CDK)
    if ! command_exists node; then
        missing_deps+=("nodejs")
    fi
    
    # Check npm
    if ! command_exists npm; then
        missing_deps+=("npm")
    fi
    
    # Check Docker (optional)
    if ! command_exists docker; then
        print_warning "Docker not found. Local development with Docker Compose will not be available."
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        print_status "Please install the missing dependencies:"
        echo ""
        echo "Ubuntu/Debian:"
        echo "  sudo apt update"
        echo "  sudo apt install python3 python3-pip nodejs npm"
        echo "  curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'"
        echo "  unzip awscliv2.zip"
        echo "  sudo ./aws/install"
        echo ""
        echo "macOS:"
        echo "  brew install python3 node awscli"
        echo ""
        echo "Windows:"
        echo "  Download and install from:"
        echo "  - Python: https://www.python.org/downloads/"
        echo "  - Node.js: https://nodejs.org/"
        echo "  - AWS CLI: https://aws.amazon.com/cli/"
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements.txt
    
    print_success "Python dependencies installed successfully"
}

# Function to install CDK
install_cdk() {
    print_status "Installing AWS CDK..."
    
    # Check if CDK is already installed
    if ! command_exists cdk; then
        npm install -g aws-cdk
        print_success "AWS CDK installed successfully"
    else
        print_status "AWS CDK is already installed"
    fi
}

# Function to configure environment
configure_environment() {
    print_status "Configuring environment..."
    
    # Use the Python configuration script
    python scripts/configure_env.py
    
    if [ $? -ne 0 ]; then
        print_error "Environment configuration failed"
        exit 1
    fi
    
    print_success "Environment configuration completed"
}

# Function to bootstrap CDK
bootstrap_cdk() {
    print_status "Bootstrapping AWS CDK..."
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Bootstrap CDK
    cdk bootstrap
    
    print_success "CDK bootstrapped successfully"
}

# Function to deploy stacks
deploy_stacks() {
    print_status "Deploying infrastructure stacks..."
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Deploy all stacks
    cdk deploy --all --require-approval never
    
    print_success "All stacks deployed successfully"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Run tests
    python -m pytest tests/ -v
    
    print_success "Tests completed successfully"
}

# Function to show usage
show_usage() {
    echo "Enterprise Data Quality & Compliance Platform - Setup Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  setup          Complete setup (prerequisites, dependencies, configuration)"
    echo "  deploy         Deploy all infrastructure stacks"
    echo "  test           Run tests"
    echo "  bootstrap      Bootstrap CDK"
    echo "  validate       Validate AWS credentials"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup       # Complete setup"
    echo "  $0 deploy      # Deploy infrastructure"
    echo "  $0 test        # Run tests"
}

# Main script logic
main() {
    case "${1:-setup}" in
        "setup")
            print_status "Starting complete setup..."
            check_prerequisites
            validate_aws_credentials
            install_dependencies
            install_cdk
            configure_environment
            bootstrap_cdk
            print_success "Setup completed successfully!"
            print_status "Next steps:"
            echo "  1. Update .env with your security settings"
            echo "  2. Run: $0 deploy"
            echo "  3. Run: $0 test"
            ;;
        "deploy")
            validate_aws_credentials
            install_dependencies
            deploy_stacks
            ;;
        "test")
            install_dependencies
            run_tests
            ;;
        "bootstrap")
            validate_aws_credentials
            install_dependencies
            bootstrap_cdk
            ;;
        "validate")
            validate_aws_credentials
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
