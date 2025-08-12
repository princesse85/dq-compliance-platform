# Enterprise Data Quality & Compliance Platform - Project Structure

This document describes the clean and organized project structure for the Enterprise Data Quality & Compliance Platform.

## 📁 Root Directory Structure

```
enterprise-data-quality-platform/
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # Project license
├── 📄 CONTRIBUTING.md              # Contributing guidelines
├── 📄 requirements.txt             # Python dependencies
├── 📄 app.py                       # CDK application entry point
├── 📄 cdk.json                     # CDK configuration
├── 📄 Dockerfile                   # Multi-stage Docker build
├── 📄 docker-compose.yml           # Local development environment
├── 📄 Makefile                     # Development and deployment commands
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 src/                         # Source code
│   ├── 📁 data_quality/           # Data quality modules
│   ├── 📁 etl_pipelines/          # ETL pipeline modules
│   ├── 📁 ml/                     # Machine learning modules
│   ├── 📁 ocr/                    # OCR and document processing
│   ├── 📁 data/                   # Data processing utilities
│   └── 📁 utils/                  # Utility modules
│
├── 📁 infrastructure/              # Infrastructure and configuration
│   ├── 📁 stacks/                 # CDK infrastructure stacks
│   ├── 📁 config/                 # Configuration files
│   └── 📁 security/               # Security configuration
│
├── 📁 tests/                       # Test suite
│   ├── 📁 unit/                   # Unit tests
│   ├── 📁 integration/            # Integration tests
│   └── 📁 e2e/                    # End-to-end tests
│
├── 📁 docs/                        # Documentation
│   ├── 📄 README.md               # Main documentation
│   ├── 📄 deployment.md           # Deployment guide
│   ├── 📄 architecture.md         # Architecture documentation
│   ├── 📄 project-structure.md    # This file
│   └── 📄 cleanup-summary.md      # Cleanup summary
│
├── 📁 scripts/                     # Utility scripts
│   ├── 📄 setup.sh                # Setup scripts
│   ├── 📄 deploy.sh               # Deployment scripts
│   └── 📄 maintenance.sh          # Maintenance scripts
│
├── 📁 monitoring/                  # Monitoring and observability
│   ├── 📁 dashboards/             # CloudWatch dashboards
│   ├── 📁 alarms/                 # CloudWatch alarms
│   ├── 📁 grafana/                # Grafana configuration
│   └── 📁 prometheus/             # Prometheus configuration
│
├── 📁 .github/                     # GitHub configuration
│   └── 📁 workflows/              # CI/CD workflows
│
├── 📁 assets/                      # Static assets
│   ├── 📁 images/                 # Images and diagrams
│   ├── 📁 templates/              # Template files
│   └── 📁 samples/                # Sample data files
│
├── 📁 analytics/                   # Analytics outputs
│   ├── 📁 reports/                # Generated reports
│   ├── 📁 metrics/                # Performance metrics
│   └── 📁 visualizations/         # Data visualizations
│
├── 📁 lambda_app/                  # Lambda function code
│   ├── 📁 handlers/               # Lambda handlers
│   └── 📁 layers/                 # Lambda layers
│
└── 📁 .venv/                       # Virtual environment (gitignored)
```

## 📁 Source Code Structure (`src/`)

### Data Quality Modules (`src/data_quality/`)

```
src/data_quality/
├── 📄 __init__.py
├── 📄 quality_assessment.py       # Data quality assessment logic
├── 📄 quality_metrics.py          # Quality metrics calculation
├── 📄 quality_rules.py            # Data quality rules
├── 📄 quality_reports.py          # Quality report generation
└── 📄 generate_synthetic_data.py  # Test data generation
```

### ETL Pipelines (`src/etl_pipelines/`)

```
src/etl_pipelines/
├── 📄 __init__.py
├── 📄 contracts_etl_job.py        # Contracts ETL processing
├── 📄 data_cleaning.py            # Data cleaning utilities
├── 📄 data_transformation.py      # Data transformation logic
└── 📄 pipeline_monitoring.py      # Pipeline monitoring
```

### Machine Learning (`src/ml/`)

```
src/ml/
├── 📄 __init__.py
├── 📁 pipeline/                   # ML pipeline components
│   ├── 📄 legal_ml_pipeline.py    # Legal document ML pipeline
│   └── 📄 model_training.py       # Model training utilities
├── 📁 models/                     # Model implementations
│   ├── 📄 baseline_tf_idf.py      # Baseline TF-IDF model
│   ├── 📄 transformer_train.py    # Transformer model training
│   └── 📄 model_evaluation.py     # Model evaluation
├── 📁 explain/                    # Model explainability
│   ├── 📄 lime_explain.py         # LIME explanations
│   └── 📄 global_words.py         # Global word importance
└── 📁 utils/                      # ML utilities
    ├── 📄 mlflow_tracker.py       # MLflow integration
    └── 📄 model_utils.py          # Model utilities
```

### OCR and Document Processing (`src/ocr/`)

```
src/ocr/
├── 📄 __init__.py
├── 📄 common.py                   # Common OCR utilities
├── 📄 lambda_ingest_router.py     # Document ingestion router
└── 📄 lambda_textract_consumer.py # Textract processing
```

### Data Processing (`src/data/`)

```
src/data/
├── 📄 __init__.py
├── 📁 generators/                 # Data generators
│   ├── 📄 legal_text_generator.py # Legal text generation
│   └── 📄 synthetic_data.py       # Synthetic data generation
├── 📄 prepare_text_corpus.py      # Text corpus preparation
└── 📄 data_utils.py               # Data utilities
```

### Utilities (`src/utils/`)

```
src/utils/
├── 📄 __init__.py
└── 📄 logging_config.py           # Logging configuration
```

## 📁 Infrastructure Structure (`infrastructure/`)

### CDK Stacks (`infrastructure/stacks/`)

```
infrastructure/stacks/
├── 📄 foundation_stack.py         # Foundation infrastructure
├── 📄 data_quality_stack.py       # Data quality platform
├── 📄 document_processing_stack.py # Document processing
├── 📄 ml_inference_stack.py       # ML inference
└── 📄 billing_alarm_stack.py      # Billing and cost management
```

### Configuration (`infrastructure/config/`)

```
infrastructure/config/
├── 📄 production.py               # Production configuration
├── 📄 staging.py                  # Staging configuration
└── 📄 development.py              # Development configuration
```

### Security (`infrastructure/security/`)

```
infrastructure/security/
├── 📄 security_config.py          # Security configuration
├── 📄 iam_policies.py             # IAM policies
└── 📄 compliance_frameworks.py    # Compliance frameworks
```

## 📁 Test Structure (`tests/`)

```
tests/
├── 📄 __init__.py
├── 📄 conftest.py                 # Pytest configuration
├── 📁 unit/                       # Unit tests
│   ├── 📁 data_quality/           # Data quality unit tests
│   ├── 📁 ml/                     # ML unit tests
│   └── 📁 utils/                  # Utility unit tests
├── 📁 integration/                # Integration tests
│   ├── 📁 aws/                    # AWS integration tests
│   └── 📁 api/                    # API integration tests
└── 📁 e2e/                        # End-to-end tests
    ├── 📁 deployment/             # Deployment tests
    └── 📁 workflows/              # Workflow tests
```

## 📁 Documentation Structure (`docs/`)

```
docs/
├── 📄 README.md                   # Main documentation
├── 📄 deployment.md               # Deployment guide
├── 📄 architecture.md             # Architecture documentation
├── 📄 project-structure.md        # This file
├── 📄 cleanup-summary.md          # Cleanup summary
├── 📄 api.md                      # API documentation
├── 📄 troubleshooting.md          # Troubleshooting guide
└── 📄 contributing.md             # Contributing guidelines
```

## 📁 Monitoring Structure (`monitoring/`)

```
monitoring/
├── 📁 dashboards/                 # CloudWatch dashboards
│   ├── 📄 production.json         # Production dashboard
│   ├── 📄 staging.json            # Staging dashboard
│   └── 📄 development.json        # Development dashboard
├── 📁 alarms/                     # CloudWatch alarms
│   ├── 📄 production.json         # Production alarms
│   ├── 📄 staging.json            # Staging alarms
│   └── 📄 development.json        # Development alarms
├── 📁 grafana/                    # Grafana configuration
│   ├── 📁 dashboards/             # Grafana dashboards
│   └── 📁 datasources/            # Grafana data sources
└── 📁 prometheus/                 # Prometheus configuration
    ├── 📄 prometheus.yml          # Prometheus config
    └── 📄 rules/                  # Prometheus rules
```

## 📁 Scripts Structure (`scripts/`)

```
scripts/
├── 📄 setup.sh                    # Environment setup
├── 📄 deploy.sh                   # Deployment scripts
├── 📄 maintenance.sh              # Maintenance scripts
├── 📄 backup.sh                   # Backup scripts
├── 📄 monitoring.sh               # Monitoring scripts
└── 📄 security.sh                 # Security scripts
```

## 📁 Assets Structure (`assets/`)

```
assets/
├── 📁 images/                     # Images and diagrams
│   ├── 📄 architecture.png        # Architecture diagram
│   ├── 📄 data-flow.png           # Data flow diagram
│   └── 📄 deployment.png          # Deployment diagram
├── 📁 templates/                  # Template files
│   ├── 📄 email_templates/        # Email templates
│   └── 📄 report_templates/       # Report templates
└── 📁 samples/                    # Sample data files
    ├── 📄 contracts/              # Sample contracts
    └── 📄 reports/                # Sample reports
```

## 📁 Analytics Structure (`analytics/`)

```
analytics/
├── 📁 reports/                    # Generated reports
│   ├── 📁 quality/                # Quality reports
│   ├── 📁 performance/            # Performance reports
│   └── 📁 compliance/             # Compliance reports
├── 📁 metrics/                    # Performance metrics
│   ├── 📄 data_quality.json       # Data quality metrics
│   ├── 📄 model_performance.json  # Model performance metrics
│   └── 📄 system_metrics.json     # System metrics
└── 📁 visualizations/             # Data visualizations
    ├── 📄 charts/                 # Charts and graphs
    └── 📄 dashboards/             # Interactive dashboards
```

## 📁 Lambda App Structure (`lambda_app/`)

```
lambda_app/
├── 📁 handlers/                   # Lambda handlers
│   ├── 📄 data_quality_handler.py # Data quality Lambda
│   ├── 📄 ml_inference_handler.py # ML inference Lambda
│   └── 📄 document_handler.py     # Document processing Lambda
├── 📁 layers/                     # Lambda layers
│   ├── 📁 dependencies/           # Dependency layers
│   └── 📁 custom/                 # Custom layers
└── 📄 requirements.txt            # Lambda dependencies
```

## 🔧 Key Configuration Files

### Root Level

- **`app.py`**: CDK application entry point
- **`cdk.json`**: CDK configuration
- **`requirements.txt`**: Python dependencies
- **`Dockerfile`**: Container configuration
- **`docker-compose.yml`**: Local development
- **`Makefile`**: Development commands
- **`.gitignore`**: Git ignore rules

### Infrastructure

- **`infrastructure/config/production.py`**: Production settings
- **`infrastructure/security/security_config.py`**: Security settings
- **`infrastructure/stacks/*.py`**: CDK infrastructure stacks

### CI/CD

- **`.github/workflows/ci.yml`**: GitHub Actions workflow
- **`scripts/deploy.sh`**: Deployment scripts
- **`scripts/setup.sh`**: Environment setup

## 🎯 Benefits of This Structure

### 1. **Clear Separation of Concerns**

- Source code, infrastructure, and documentation are clearly separated
- Each module has a specific responsibility
- Easy to locate and maintain code

### 2. **Scalability**

- Modular structure supports team growth
- Easy to add new features and modules
- Clear boundaries between components

### 3. **Maintainability**

- Consistent naming conventions
- Logical grouping of related files
- Easy to understand and navigate

### 4. **Deployment Ready**

- Infrastructure as code with CDK
- Environment-specific configurations
- Automated deployment pipelines

### 5. **Testing Support**

- Dedicated test structure
- Unit, integration, and e2e tests
- Comprehensive test coverage

### 6. **Documentation**

- Comprehensive documentation structure
- Architecture and deployment guides
- API and troubleshooting documentation

### 7. **Monitoring and Observability**

- Dedicated monitoring structure
- CloudWatch and Grafana integration
- Comprehensive alerting

## 🚀 Getting Started

1. **Clone the repository**
2. **Review the structure**: Understand the organization
3. **Set up environment**: Follow the setup guide
4. **Deploy infrastructure**: Use the deployment scripts
5. **Run tests**: Verify everything works
6. **Start development**: Begin adding features

This structure provides a solid foundation for enterprise-scale development while maintaining clarity and organization.
