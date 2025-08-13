# 🚀 Quick Setup Guide

## Prerequisites

- Python 3.8+
- Node.js 16+ (for AWS CDK)
- AWS CLI configured
- Git

## Option 1: Complete AWS Deployment

```bash
# 1. Clone and setup
git clone https://github.com/princesse85/dq-compliance-platform.git
cd dq-compliance-platform
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure AWS
aws configure
npm install -g aws-cdk
cdk bootstrap

# 3. Deploy infrastructure
python scripts/configure_env.py
cdk deploy --all

# 4. Run pipelines
python scripts/generate_data_and_train.py
python src/etl_pipelines/contracts_etl_job.py

# 5. Start dashboard
make dashboard
# or: streamlit run src/dashboard/main.py
```

## Option 2: Local Development (No AWS)

```bash
# 1. Clone and setup
git clone https://github.com/princesse85/dq-compliance-platform.git
cd dq-compliance-platform
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Run dashboard
streamlit run streamlit_app.py
```

## Option 3: Using Makefile

```bash
# View all commands
make help

# Complete setup
make dev-setup

# Run dashboard
make dashboard

# Deploy to AWS
make deploy
```

## Access Points

- **Dashboard**: http://localhost:8501
- **API Endpoints**: Available after AWS deployment
- **ML Models**: Stored in S3 and loaded via Lambda

## Troubleshooting

```bash
# Check dependencies
python scripts/run_dashboard.py --check-deps

# Verify AWS credentials
aws sts get-caller-identity

# Reset environment
make reset
```

For detailed instructions, see [README.md](README.md).
