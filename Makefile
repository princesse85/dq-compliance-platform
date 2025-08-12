# Enterprise Data Quality & Compliance Platform Makefile

.PHONY: help install test lint format clean deploy destroy bootstrap

# Default target
help:
	@echo "Enterprise Data Quality & Compliance Platform"
	@echo "============================================="
	@echo ""
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  clean       - Clean temporary files"
	@echo "  bootstrap   - Bootstrap CDK"
	@echo "  deploy      - Deploy all stacks"
	@echo "  destroy     - Destroy all stacks"
	@echo "  logs        - View CloudWatch logs"
	@echo "  docs        - Build documentation"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Run tests
test:
	@echo "Running tests..."
	python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo "✅ Tests completed"

# Run linting
lint:
	@echo "Running linting..."
	flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503
	mypy src/ --ignore-missing-imports
	@echo "✅ Linting completed"

# Format code
format:
	@echo "Formatting code..."
	black src/ tests/ --line-length=100
	isort src/ tests/
	@echo "✅ Code formatting completed"

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf cdk.out/ 2>/dev/null || true
	rm -rf logs/ 2>/dev/null || true
	@echo "✅ Cleanup completed"

# Bootstrap CDK
bootstrap:
	@echo "Bootstrapping CDK..."
	cdk bootstrap
	@echo "✅ CDK bootstrapped"

# Deploy all stacks
deploy:
	@echo "Deploying all stacks..."
	cdk deploy --all --require-approval never
	@echo "✅ All stacks deployed"

# Deploy specific stack
deploy-%:
	@echo "Deploying stack: $*"
	cdk deploy enterprise-$* --require-approval never
	@echo "✅ Stack $* deployed"

# Destroy all stacks
destroy:
	@echo "Destroying all stacks..."
	cdk destroy --all --force
	@echo "✅ All stacks destroyed"

# View CloudWatch logs
logs:
	@echo "Viewing CloudWatch logs..."
	aws logs tail /aws/enterprise-dq/production --follow

# Build documentation
docs:
	@echo "Building documentation..."
	cd docs && make html
	@echo "✅ Documentation built"

# Generate test data
generate-data:
	@echo "Generating test data..."
	python src/data_quality/generate_synthetic_data.py
	@echo "✅ Test data generated"

# Run data pipeline
run-pipeline:
	@echo "Running data pipeline..."
	python src/data_quality/run_quality_assessment.py
	@echo "✅ Data pipeline completed"

# Security scan
security-scan:
	@echo "Running security scan..."
	safety check
	bandit -r src/ -f json -o security-report.json
	@echo "✅ Security scan completed"

# Performance test
perf-test:
	@echo "Running performance tests..."
	python -m pytest tests/performance/ -v
	@echo "✅ Performance tests completed"

# Production deployment
deploy-prod:
	@echo "Deploying to production..."
	export ENV_NAME=production
	cdk deploy --all --require-approval never --context env_name=production
	@echo "✅ Production deployment completed"

# Staging deployment
deploy-staging:
	@echo "Deploying to staging..."
	export ENV_NAME=staging
	cdk deploy --all --require-approval never --context env_name=staging
	@echo "✅ Staging deployment completed"

# Development setup
dev-setup: install bootstrap
	@echo "Development environment setup completed"

# Pre-commit checks
pre-commit: format lint test
	@echo "✅ Pre-commit checks passed"

# Full CI pipeline
ci: clean install lint test security-scan
	@echo "✅ CI pipeline completed"
