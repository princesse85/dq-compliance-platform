# 🏢 Enterprise Compliance Dashboard

A comprehensive, real-time dashboard for data quality and compliance monitoring built with Streamlit.

## ✨ Features

### 🚀 **Interactive Dashboard**

- **Real-time Auto-refresh**: Configurable intervals (15s to 5min)
- **Multi-select Filters**: Risk categories, regions, and risk levels
- **Dynamic Data Loading**: Cached data loading for optimal performance
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### 📊 **Analytics & Visualization**

- **Executive Dashboard**: Key performance indicators with trend analysis
- **Risk Analytics**: Deep dive into risk register with interactive tables
- **Document Intelligence**: AI-powered document analysis (PDF, TXT)
- **ML Performance Monitoring**: Real-time model performance tracking
- **Data Quality Metrics**: Comprehensive data quality assessment

### 🎨 **Enhanced UI/UX**

- **Professional Styling**: Modern, clean interface with dark sidebar
- **Animated Components**: Hover effects and smooth transitions
- **Status Indicators**: Real-time feedback and loading states
- **Export Functionality**: Data export capabilities (ready for implementation)

### 🔧 **Technical Features**

- **Modular Architecture**: Clean, maintainable code structure
- **AWS Integration**: Ready for production deployment with S3
- **Caching**: Optimized performance with Streamlit caching
- **Error Handling**: Robust error handling and fallbacks

## 🏗️ Project Structure

```
dq-compliance-platform/
├── streamlit_app.py          # Streamlit Cloud entry point
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── .gitignore              # Git ignore rules
├── src/
│   ├── dashboard/           # Streamlit dashboard
│   ├── ml/                 # Machine learning models
│   ├── etl_pipelines/      # Data processing
│   └── data_quality/       # Data validation
├── infrastructure/          # AWS CDK stacks
├── lambda_app/             # AWS Lambda functions
├── scripts/                # Deployment and setup scripts
└── assets/                 # Static assets (images, etc.)
```

## 🚀 Quick Start

### Prerequisites

Before starting, ensure you have:

- **Python 3.8+**
- **Node.js 16+** (for AWS CDK)
- **AWS CLI** configured with credentials
- **Git**

### Option 1: Complete AWS Deployment

#### 1. **Clone and Setup Environment**

```bash
# Clone the repository
git clone https://github.com/princesse85/dq-compliance-platform.git
cd dq-compliance-platform

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. **Configure AWS**

```bash
# Configure AWS credentials
aws configure

# Install AWS CDK globally
npm install -g aws-cdk

# Bootstrap CDK (first time only)
cdk bootstrap
```

#### 3. **Environment Configuration**

```bash
# Run the configuration script
python scripts/configure_env.py

# Copy and configure environment file
cp config/environment.example .env
# Edit .env with your specific settings
```

#### 4. **Deploy Infrastructure**

```bash
# Deploy all AWS infrastructure stacks
cdk deploy --all

# This will create:
# - S3 buckets for data storage
# - Lambda functions for ETL and ML inference
# - API Gateway for REST APIs
# - CloudWatch for monitoring
# - IAM roles and policies
```

#### 5. **Run ETL and ML Pipelines**

```bash
# Generate synthetic data and train models
python scripts/generate_data_and_train.py

# Run ETL pipeline
python src/etl_pipelines/contracts_etl_job.py
```

#### 6. **Run the Dashboard**

```bash
# Option 1: Using the Makefile
make dashboard

# Option 2: Using the script directly
python scripts/run_dashboard.py

# Option 3: Direct Streamlit command
streamlit run src/dashboard/main.py
```

### Option 2: Local Development (No AWS)

For quick local development without AWS deployment:

```bash
# 1. Clone and setup
git clone https://github.com/princesse85/dq-compliance-platform.git
cd dq-compliance-platform

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run dashboard with local data
streamlit run streamlit_app.py

# 5. Open browser at http://localhost:8501
```

### Option 3: Using Makefile Commands

```bash
# View all available commands
make help

# Complete setup
make dev-setup

# Run dashboard
make dashboard

# Run tests
make test

# Deploy to AWS
make deploy

# Clean up
make clean
```

## 🔧 Configuration

### Environment Variables

For production deployment, set these environment variables:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Dashboard Configuration
COMPLIANCE_BUCKET=your-s3-bucket-name
```

### Customization

The dashboard is highly customizable:

- **Data Sources**: Modify `src/dashboard/utils.py` to connect to your data sources
- **Styling**: Update CSS in `src/dashboard/main.py`
- **Charts**: Customize visualizations in the chart functions
- **Filters**: Add new filter options in the sidebar

## 📊 Dashboard Sections

### 1. Executive Dashboard

- **KPIs**: Overall compliance, risk scores, high-risk items, ML accuracy
- **Charts**: Risk distribution, regional heatmap, compliance trends
- **Real-time Updates**: Auto-refresh with configurable intervals

### 2. Risk Analytics

- **Interactive Table**: Sortable risk register with progress indicators
- **Multi-level Filtering**: By category, region, and risk level
- **Data Export**: Export filtered data (ready for implementation)

### 3. Document Intelligence

- **File Upload**: Support for PDF and TXT files
- **AI Analysis**: Compliance scoring, risk assessment, entity extraction
- **Detailed Reports**: Key risks, recommendations, and extracted entities

### 4. ML Performance

- **Model Monitoring**: Accuracy, precision, recall, and latency tracking
- **Performance Trends**: Historical performance visualization
- **Model Selection**: Compare different ML models

### 5. Data Quality

- **Quality Metrics**: Completeness, accuracy, timeliness, validity
- **Trend Analysis**: Quality score changes over time
- **Issue Detection**: Automated quality issue identification

## 🛠️ Development

### Adding New Features

1. **New Data Source**

   ```python
   # In src/dashboard/utils.py
   def load_new_data():
       # Your data loading logic
       pass
   ```

2. **New Chart**

   ```python
   # In src/dashboard/main.py
   def create_new_chart(data):
       # Your chart creation logic
       pass
   ```

3. **New Tab**
   ```python
   # Add to main() function
   with tab6:
       show_new_feature_tab()
   ```

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test categories
make test-unit
make test-integration
make test-performance
```

## 🔒 Security

- **Environment Variables**: Sensitive data stored in environment variables
- **Input Validation**: All user inputs are validated
- **Error Handling**: Secure error messages without exposing internals
- **AWS IAM**: Proper IAM roles and permissions for production

## 📈 Performance

- **Caching**: Streamlit caching for expensive operations
- **Lazy Loading**: Data loaded only when needed
- **Optimized Queries**: Efficient data filtering and aggregation
- **Responsive Design**: Fast loading on all devices

## 🚨 Troubleshooting

### Common Issues

```bash
# Check dependencies
python scripts/run_dashboard.py --check-deps

# Verify AWS credentials
aws sts get-caller-identity

# Check CDK status
cdk diff

# View logs
make logs

# Reset environment
make reset
```

### Error Solutions

- **AWS Credentials**: Ensure `aws configure` is completed
- **CDK Bootstrap**: Run `cdk bootstrap` if deploying for first time
- **Port Conflicts**: Change port with `--port 8502` if 8501 is busy
- **Dependencies**: Run `pip install -r requirements.txt` if import errors occur

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the inline code comments
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Email**: contact@company.com

## 🔄 Version History

### v2.1.0 (Current)

- ✅ Real-time auto-refresh functionality
- ✅ Multi-select filters for enhanced data exploration
- ✅ Enhanced visual feedback and animations
- ✅ Modular architecture for better maintainability
- ✅ Streamlit Cloud deployment ready
- ✅ Professional dark sidebar theme
- ✅ Export functionality framework
- ✅ Complete AWS infrastructure deployment
- ✅ ETL and ML pipeline integration

### v2.0.0

- ✅ Initial dashboard implementation
- ✅ Basic charts and visualizations
- ✅ AWS integration framework
- ✅ Document analysis capabilities

### v1.0.0

- ✅ Core compliance monitoring features
- ✅ Basic risk analytics
- ✅ ML model integration

---

**Built with ❤️ by the Enterprise Solutions Team**
