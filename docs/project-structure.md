# Project Structure

## Overview

The Enterprise Data Quality Platform follows a modular, production-ready architecture with clear separation of concerns and enterprise-grade organization.

## Directory Structure

```
enterprise-data-quality-platform/
├── 📁 docs/                          # Documentation
│   ├── architecture.md               # Architecture overview
│   └── project-structure.md          # This file
├── 📁 src/                           # Source code
│   ├── 📁 data_quality/              # Data quality framework
│   │   ├── __init__.py
│   │   ├── data_validation_suite.py  # Great Expectations validation
│   │   ├── generate_synthetic_data.py # Test data generation
│   │   ├── quality_assessment.py     # Quality scoring and monitoring
│   │   └── utils.py                  # Validation utilities
│   ├── 📁 etl_pipelines/             # ETL processing
│   │   ├── __init__.py
│   │   └── contracts_etl_job.py      # Glue ETL job for contracts
│   ├── 📁 machine_learning/          # ML capabilities
│   │   ├── __init__.py
│   │   ├── baseline_tf_idf.py        # Baseline ML model
│   │   ├── eval_report.py            # Model evaluation
│   │   ├── mlflow_utils.py           # MLflow integration
│   │   ├── transformer_train.py      # Transformer model training
│   │   └── 📁 explain/               # Model explainability
│   │       ├── global_words.py       # Global feature importance
│   │       └── lime_explain.py       # LIME explanations
│   └── 📁 data/                      # Data preparation
│       └── prepare_text_corpus.py    # Text corpus preparation
├── 📁 stacks/                        # AWS CDK infrastructure
│   ├── foundation_stack.py           # Core infrastructure
│   ├── data_quality_stack.py         # Data quality components
│   ├── billing_alarm_stack.py        # Cost monitoring
│   └── ml_inference_stack.py         # ML inference API
├── 📁 tests/                         # Test suite
├── 📁 lambda_app/                    # Lambda application
│   ├── app/                          # Lambda function code
│   ├── Dockerfile                    # Container definition
│   ├── requirements.txt              # Lambda dependencies
│   ├── build_and_deploy.sh           # Deployment script
│   └── test_api.py                   # API testing
├── 📁 assets/                        # Static assets
│   ├── sample_contract_register.csv  # Sample data
│   └── image_showcase.png            # Documentation images
├── 📁 data/                          # Data directories
│   ├── raw/                          # Raw data storage
│   ├── processed/                    # Processed data storage
│   └── text_corpus/                  # ML training data
├── 📁 analytics/                     # Analytics outputs
│   └── models/                       # Trained models
├── 📁 mlruns/                        # MLflow experiment tracking
├── 📁 cdk.out/                       # CDK build outputs
├── 📄 README.md                      # Main documentation
├── 📄 CONTRIBUTING.md                # Contribution guidelines
├── 📄 LICENSE                        # MIT License
├── 📄 requirements.txt               # Python dependencies
├── 📄 env.example                    # Environment variables template
├── 📄 cdk.json                       # CDK configuration
├── 📄 app.py                         # CDK application entry point
└── 📄 .gitignore                     # Git ignore rules
```

## Key Components

### Infrastructure (CDK Stacks)

#### Foundation Stack (`stacks/foundation_stack.py`)

- **S3 Buckets**: Raw, processed, analytics data lakes
- **IAM Roles**: Admin, Data Engineer, Reviewer groups
- **CloudTrail**: Audit logging and compliance
- **Glue Database**: Data catalog foundation

#### Data Quality Stack (`stacks/data_quality_stack.py`)

- **Glue Crawlers**: Automatic schema discovery
- **ETL Jobs**: Data transformation pipelines
- **IAM Roles**: Glue service permissions
- **Quality Framework**: Great Expectations integration

#### Billing Alarm Stack (`stacks/billing_alarm_stack.py`)

- **Budget Alerts**: Cost monitoring and notifications
- **SNS Topics**: Alert distribution
- **CloudWatch**: Billing metrics and alarms

#### ML Inference Stack (`stacks/ml_inference_stack.py`)

- **Lambda Functions**: Model serving
- **API Gateway**: RESTful API endpoints
- **ECR Repository**: Container image storage
- **SSM Parameters**: Configuration management

### Data Quality Framework (`src/data_quality/`)

#### Core Components

- **Validation Suite**: Great Expectations validation rules
- **Quality Assessment**: Automated quality scoring
- **Synthetic Data**: Test data generation
- **Utilities**: Validation helper functions

#### Features

- Automated data validation
- Quality score calculation
- Compliance monitoring
- Audit trail generation

### ETL Pipelines (`src/etl_pipelines/`)

#### Processing Jobs

- **Contracts ETL**: Contract data transformation
- **Data Cleaning**: Standardization and validation
- **Schema Evolution**: Automatic schema updates
- **Quality Gates**: Validation checkpoints

### Machine Learning (`src/machine_learning/`)

#### Model Development

- **Baseline Models**: TF-IDF based classifiers
- **Transformer Models**: Advanced NLP models
- **Model Evaluation**: Performance assessment
- **Explainability**: Model interpretation tools

#### ML Operations

- **MLflow Integration**: Experiment tracking
- **Model Registry**: Version control
- **A/B Testing**: Model comparison
- **Monitoring**: Performance tracking

### Lambda Application (`lambda_app/`)

#### API Services

- **Model Serving**: Real-time inference
- **Explanation API**: Model interpretability
- **Health Checks**: Service monitoring
- **Error Handling**: Robust error management

## Configuration Management

### Environment Variables (`env.example`)

- **AWS Configuration**: Region, profile settings
- **Project Settings**: Prefix, environment names
- **Data Lake**: Bucket configurations
- **Quality Settings**: Thresholds and parameters
- **ML Configuration**: Model and training settings
- **Security**: Encryption and access controls

### CDK Configuration (`cdk.json`)

- **Project Context**: Environment-specific settings
- **Resource Naming**: Consistent naming conventions
- **Budget Controls**: Cost management settings
- **Environment Support**: Multi-environment deployment

## Development Workflow

### Local Development

1. **Environment Setup**: Virtual environment and dependencies
2. **Configuration**: Environment variables and AWS setup
3. **Testing**: Unit, integration, and e2e tests
4. **Code Quality**: Linting, formatting, and type checking

### Deployment Pipeline

1. **Infrastructure**: CDK deployment to target environment
2. **Data Pipeline**: ETL job execution and validation
3. **Quality Assessment**: Automated quality checks
4. **Monitoring**: Performance and cost monitoring

### Quality Assurance

- **Code Review**: Pull request process
- **Testing**: Automated test suites
- **Documentation**: Comprehensive documentation
- **Security**: Security scanning and compliance

## Best Practices

### Code Organization

- **Modular Design**: Clear separation of concerns
- **Type Hints**: Comprehensive type annotations
- **Documentation**: Docstrings and comments
- **Error Handling**: Robust error management

### Security

- **Least Privilege**: Minimal required permissions
- **Encryption**: Data encryption at rest and in transit
- **Audit Logging**: Comprehensive audit trails
- **Access Control**: Role-based access management

### Performance

- **Optimization**: Efficient data processing
- **Monitoring**: Real-time performance tracking
- **Scaling**: Auto-scaling capabilities
- **Cost Management**: Resource optimization

### Compliance

- **Data Governance**: Data lineage and tracking
- **Quality Assurance**: Automated quality validation
- **Audit Trails**: Complete audit logging
- **Regulatory Compliance**: GDPR, SOX, HIPAA support

