# Enterprise Data Quality & Compliance Platform

A comprehensive, production-ready data quality and compliance platform built on AWS, designed for enterprise-scale data governance, quality monitoring, and regulatory compliance.

## 🏗️ Architecture Overview

This platform implements a modern data architecture with the following components:

- **Data Lake**: Multi-zone S3-based data lake (Raw → Processed → Analytics)
- **Data Processing**: AWS Glue ETL jobs with PySpark
- **Data Quality**: Great Expectations validation framework
- **Monitoring**: CloudWatch metrics and S3-based quality logs
- **Security**: IAM roles, CloudTrail audit logging, and encryption
- **Cost Management**: Billing alarms and budget controls

## 🚀 Features

### Phase 1: Data Lake & Quality Foundation ✅

- Automated data ingestion and cataloging
- ETL pipelines with data cleaning and standardization
- Comprehensive data quality validation
- Quality scoring and monitoring
- Audit trail and compliance logging

### Phase 2: Document Processing ✅

- PDF contract processing with Amazon Textract
- OCR-based data extraction
- Document classification and routing
- Compliance rule validation
- Multi-format support (PDF/DOCX)
- Review manifest for low-confidence documents

### Phase 3: Machine Learning Pipeline (Planned)

- Automated model training and deployment
- Risk scoring and prediction
- Model monitoring and drift detection
- A/B testing framework

### Phase 4: API & Inference (Planned)

- RESTful API for real-time predictions
- Model serving with AWS Lambda
- API Gateway with authentication
- Real-time monitoring and alerting

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js 16+** - [Download here](https://nodejs.org/)
- **AWS CLI** - [Download here](https://aws.amazon.com/cli/)
- **Docker** (optional) - [Download here](https://www.docker.com/)

### Easy Deployment

#### Option 1: Automated Setup (Recommended)

**For Linux/macOS:**
```bash
git clone https://github.com/your-username/dq-compliance-platform.git
cd dq-compliance-platform
chmod +x scripts/setup.sh
./scripts/setup.sh setup
./scripts/setup.sh deploy
```

**For Windows:**
```powershell
git clone https://github.com/your-username/dq-compliance-platform.git
cd dq-compliance-platform
.\scripts\deploy.ps1 deploy
```

#### Option 2: Manual Setup

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/dq-compliance-platform.git
cd dq-compliance-platform
```

2. **Configure AWS credentials:**
```bash
aws configure
```

3. **Install dependencies:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install -g aws-cdk
```

4. **Deploy infrastructure:**
```bash
cdk bootstrap
cdk deploy --all --require-approval never
```

### What Gets Deployed

The platform deploys the following AWS infrastructure:

- **🏗️ Foundation Stack** - S3 buckets, IAM roles, VPC, CloudWatch
- **💰 Billing Alarm Stack** - Cost monitoring and alerts
- **🔍 Data Quality Stack** - Great Expectations, Glue jobs
- **🤖 ML Inference Stack** - Lambda functions, API Gateway
- **📄 Document Processing Stack** - Textract, OCR processing

### Testing Your Deployment

```bash
# Run tests
./scripts/setup.sh test  # Linux/macOS
.\scripts\deploy.ps1 test  # Windows

# Test API endpoints (get URL from CDK outputs)
curl https://your-api-gateway-url.amazonaws.com/prod/health
```

## 📋 Detailed Setup Instructions

# Deploy data quality platform
cdk deploy enterprise-data-quality --require-approval never

# Deploy billing alarms
cdk deploy enterprise-billing --require-approval never

# Deploy Document Processing
cdk deploy enterprise-document-processing --require-approval never
```

### Deploy Specific Components

```bash
# Deploy only data quality components
cdk deploy enterprise-data-quality --require-approval never

# Deploy only monitoring components
cdk deploy enterprise-monitoring --require-approval never
```

## 📊 Data Pipeline Usage

### 1. Generate Test Data

```bash
python src/data_quality/generate_synthetic_data.py
```

### 2. Upload Data

```bash
aws s3 cp assets/sample_contracts.csv s3://enterprise-raw-{env}-{account}-{region}/contracts/ingest_date=2025-01-15/
```

### 3. Run Data Pipeline

```bash
# Start data discovery
aws glue start-crawler --name enterprise-{env}-raw-contracts

# Run ETL processing
aws glue start-job-run --job-name enterprise-{env}-contracts-etl

# Start processed data discovery
aws glue start-crawler --name enterprise-{env}-processed-contracts
```

### 4. Run Quality Assessment

```bash
export RAW_BUCKET="enterprise-raw-{env}-{account}-{region}"
export ANALYTICS_BUCKET="enterprise-analytics-{env}-{account}-{region}"
export INGEST_DATE="2025-01-15"

python src/data_quality/run_quality_assessment.py
```

## 📄 Document Processing

Upload PDF/DOCX files to `raw/docs/ingest_date=YYYY-MM-DD/` and they'll be automatically processed:

```bash
# Upload documents
aws s3 cp document.pdf s3://enterprise-raw-{env}-{account}-{region}/docs/ingest_date=2025-08-12/

# Check results
aws s3 ls s3://enterprise-processed-{env}-{account}-{region}/docs/text/2025-08-12/
```

## 🔧 Configuration

### Environment Variables

- `PROJECT_PREFIX`: Project identifier (default: "enterprise")
- `ENV_NAME`: Environment name (dev, staging, prod)
- `AWS_REGION`: AWS region for deployment
- `BILLING_EMAIL`: Email for cost alerts
- `MONTHLY_BUDGET`: Monthly budget limit

### CDK Configuration

Edit `cdk.json` to customize:

- Project settings
- Environment configurations
- Resource naming conventions

## 📈 Monitoring & Observability

### CloudWatch Dashboards

- Data pipeline metrics
- Quality score trends
- Cost monitoring
- Error rates and performance

### Quality Metrics

- Data completeness scores
- Validation rule compliance
- Data freshness indicators
- Anomaly detection alerts

### Cost Monitoring

- Monthly budget alerts
- Resource utilization tracking
- Cost optimization recommendations

## 🔒 Security & Compliance

### Data Protection

- Encryption at rest and in transit
- IAM role-based access control
- VPC isolation for sensitive workloads
- Audit logging with CloudTrail

### Compliance Features

- GDPR-compliant data handling
- SOX audit trail requirements
- Data retention policies
- Access control and monitoring

## 🧪 Testing

### Unit Tests

```bash
python -m pytest tests/unit/
```

### Integration Tests

```bash
python -m pytest tests/integration/
```

### End-to-End Tests

```bash
python -m pytest tests/e2e/
```

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/enterprise-data-quality-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/enterprise-data-quality-platform/discussions)

## 🏢 Enterprise Support

For enterprise customers:

- **Email**: enterprise-support@company.com
- **Phone**: +1-XXX-XXX-XXXX
- **Slack**: #enterprise-support

---

**Built with ❤️ for enterprise data quality and compliance**
