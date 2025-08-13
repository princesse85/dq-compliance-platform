# 🚀 Complete Setup Guide

## Prerequisites

- **Python 3.8+**
- **Node.js 16+** (for AWS CDK)
- **AWS CLI** (for AWS deployment)
- **Git**

## 🎯 Quick Start (One Command Setup)

```bash
# Clone the repository
git clone https://github.com/princesse85/dq-compliance-platform.git
cd dq-compliance-platform

# Run complete setup (handles everything automatically)
python scripts/setup_complete.py
```

## 📋 Manual Setup Options

### Option 1: Complete AWS Deployment

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

# 3. Setup environment
python scripts/configure_env.py

# 4. Deploy infrastructure
cdk deploy --all

# 5. Generate data and train models
python scripts/generate_data_and_train.py

# 6. Start dashboard
streamlit run streamlit_app.py
```

### Option 2: Local Development (No AWS)

```bash
# 1. Clone and setup
git clone https://github.com/princesse85/dq-compliance-platform.git
cd dq-compliance-platform
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Setup environment
python scripts/configure_env.py

# 3. Generate data and train models
python scripts/generate_data_and_train.py

# 4. Start dashboard
streamlit run streamlit_app.py
```

### Option 3: Using Makefile

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

## 🔧 Environment Variables

The setup creates a `.env` file with all necessary configuration:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_DEFAULT_REGION=us-east-1
AWS_REGION=us-east-1

# AWS S3 Buckets
COMPLIANCE_BUCKET=enterprise-compliance-data-{account_id}
RAW_DATA_BUCKET=enterprise-raw-data-{account_id}
PROCESSED_DATA_BUCKET=enterprise-processed-data-{account_id}
ML_MODELS_BUCKET=enterprise-ml-models-{account_id}

# Dashboard Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_SERVER_HEADLESS=true
DASHBOARD_REFRESH_INTERVAL=30
DASHBOARD_MAX_UPLOAD_SIZE=200

# ML Model Configuration
MODEL_NAME=distilbert-base-uncased
EPOCHS=1
BATCH_SIZE=16
LEARNING_RATE=2e-5
MAX_LENGTH=128

# ETL Configuration
SPARK_MASTER=local[*]
SPARK_DRIVER_MEMORY=2g
SPARK_EXECUTOR_MEMORY=2g
ETL_RAW_PREFIX=contract_register/
ETL_PROCESSED_PREFIX=contract_register/

# Development Configuration
DEBUG=false
ENVIRONMENT=development
USE_LOCAL_DATA=true
MOCK_AWS_SERVICES=false

# Feature Flags
ENABLE_DOCUMENT_ANALYSIS=true
ENABLE_ML_PREDICTIONS=true
ENABLE_REAL_TIME_ALERTS=false
ENABLE_DATA_EXPORT=true
```

## 📁 Project Structure

```
dq-compliance-platform/
├── .env                          # Environment variables
├── .streamlit/config.toml        # Streamlit configuration
├── requirements.txt              # Main dependencies
├── requirements-dev.txt          # Development dependencies
├── scripts/
│   ├── setup_complete.py        # Complete setup script
│   ├── configure_env.py         # Environment configuration
│   └── generate_data_and_train.py # Data and ML setup
├── src/
│   ├── dashboard/               # Streamlit dashboard
│   ├── ml/                     # Machine learning models
│   ├── etl_pipelines/          # Data processing
│   └── data_quality/           # Data validation
├── infrastructure/              # AWS CDK stacks
├── analytics/models/            # Trained ML models
└── assets/                     # Static assets
```

## 🚀 Access Points

- **Dashboard**: http://localhost:8501
- **API Endpoints**: Available after AWS deployment
- **ML Models**: Stored in S3 and loaded via Lambda

## 🔍 Troubleshooting

### Common Issues

```bash
# Check dependencies
python scripts/run_dashboard.py --check-deps

# Verify AWS credentials
aws sts get-caller-identity

# Check CDK status
cdk diff

# Reset environment
make reset

# View logs
make logs
```

### Error Solutions

- **AWS Credentials**: Ensure `aws configure` is completed
- **CDK Bootstrap**: Run `cdk bootstrap` if deploying for first time
- **Port Conflicts**: Change port with `--port 8502` if 8501 is busy
- **Dependencies**: Run `pip install -r requirements.txt` if import errors occur
- **PySpark Issues**: ETL will fallback to pandas if PySpark not available
- **ML Training Issues**: Models will use mock data if training fails

## 📊 What Gets Set Up

### ✅ Environment

- Virtual environment creation
- Dependency installation
- Environment variable configuration
- Directory structure creation

### ✅ AWS Infrastructure (if configured)

- S3 buckets for data storage
- Lambda functions for ETL and ML
- API Gateway for REST APIs
- CloudWatch for monitoring
- IAM roles and policies

### ✅ Data & ML

- Synthetic compliance data generation
- Baseline TF-IDF model training
- Transformer model training (if dependencies available)
- Real ML integration with dashboard

### ✅ Dashboard

- Streamlit configuration
- Professional UI setup
- Real-time data loading
- ML prediction integration

## 🎯 Next Steps

After setup completion:

1. **For AWS Deployment**:

   - Update `.env` with your AWS credentials
   - Run `cdk deploy --all`
   - Access dashboard at deployed URL

2. **For Local Development**:

   - Run `streamlit run streamlit_app.py`
   - Access dashboard at http://localhost:8501

3. **For Production**:
   - Update security settings in `.env`
   - Configure monitoring and alerts
   - Set up CI/CD pipeline

For detailed instructions, see [README.md](README.md).
