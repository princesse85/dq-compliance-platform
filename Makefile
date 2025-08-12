# =============================================================================
# DATA QUALITY COMPLIANCE PLATFORM - MAKEFILE
# =============================================================================

# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
COVERAGE := coverage
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# Project configuration
PROJECT_NAME := enterprise-data-quality
ENV_NAME ?= development
AWS_REGION ?= us-east-1

# Test configuration
TEST_DIR := tests
COVERAGE_DIR := htmlcov
COVERAGE_REPORT := coverage.xml
TEST_RESULTS := test-results.xml
PERFORMANCE_RESULTS := performance-results.xml

# Dashboard configuration
DASHBOARD_PORT ?= 8501
DASHBOARD_HOST ?= localhost

# =============================================================================
# DEVELOPMENT COMMANDS
# =============================================================================

.PHONY: help
help: ## Show this help message
	@echo "Data Quality Compliance Platform - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install project dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

.PHONY: install-dev
install-dev: ## Install development dependencies
	$(PIP) install pytest pytest-cov pytest-mock pytest-xdist pytest-html
	$(PIP) install moto psutil black flake8 mypy

.PHONY: clean
clean: ## Clean build artifacts and temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage
	rm -rf $(COVERAGE_DIR) $(COVERAGE_REPORT) $(TEST_RESULTS) $(PERFORMANCE_RESULTS)

# =============================================================================
# DASHBOARD COMMANDS
# =============================================================================

.PHONY: dashboard
dashboard: ## Run the Streamlit dashboard
	$(PYTHON) scripts/run_dashboard.py --port $(DASHBOARD_PORT) --host $(DASHBOARD_HOST)

.PHONY: dashboard-dev
dashboard-dev: ## Run dashboard in development mode
	STREAMLIT_SERVER_HEADLESS=false $(PYTHON) scripts/run_dashboard.py --port $(DASHBOARD_PORT) --host $(DASHBOARD_HOST)

.PHONY: dashboard-check
dashboard-check: ## Check dashboard dependencies
	$(PYTHON) scripts/run_dashboard.py --check-deps

.PHONY: dashboard-build
dashboard-build: ## Build dashboard for production
	$(PYTHON) -m streamlit config show > .streamlit/config.toml
	@echo "Dashboard configuration generated"

.PHONY: dashboard-deploy
dashboard-deploy: ## Deploy dashboard to production
	@echo "Deploying dashboard to production..."
	$(PYTHON) scripts/run_dashboard.py --port 8501 --host 0.0.0.0

# =============================================================================
# TESTING COMMANDS
# =============================================================================

.PHONY: test
test: ## Run all tests
	$(PYTEST) $(TEST_DIR) -v

.PHONY: test-unit
test-unit: ## Run unit tests only
	$(PYTEST) $(TEST_DIR)/unit/ -v -m unit

.PHONY: test-integration
test-integration: ## Run integration tests only
	$(PYTEST) $(TEST_DIR)/integration/ -v -m integration

.PHONY: test-performance
test-performance: ## Run performance tests only
	$(PYTEST) $(TEST_DIR)/performance/ -v -m performance

.PHONY: test-aws
test-aws: ## Run AWS integration tests
	$(PYTEST) $(TEST_DIR)/integration/test_aws_integration.py -v -m aws

.PHONY: test-e2e
test-e2e: ## Run end-to-end tests
	$(PYTEST) $(TEST_DIR)/integration/test_end_to_end.py -v -m slow

.PHONY: test-fast
test-fast: ## Run fast tests (unit + integration, excluding slow tests)
	$(PYTEST) $(TEST_DIR) -v -m "not slow"

.PHONY: test-coverage
test-coverage: ## Run tests with coverage report
	$(PYTEST) $(TEST_DIR) --cov=src --cov=infrastructure \
		--cov-report=term-missing \
		--cov-report=html:$(COVERAGE_DIR) \
		--cov-report=xml:$(COVERAGE_REPORT) \
		--cov-fail-under=80

.PHONY: test-parallel
test-parallel: ## Run tests in parallel
	$(PYTEST) $(TEST_DIR) -n auto

.PHONY: test-debug
test-debug: ## Run tests with debug output
	$(PYTEST) $(TEST_DIR) -v -s --tb=long

.PHONY: test-specific
test-specific: ## Run specific test file (usage: make test-specific FILE=test_file.py)
	$(PYTEST) $(TEST_DIR)/$(FILE) -v

.PHONY: test-smoke
test-smoke: ## Run smoke tests for basic functionality
	$(PYTEST) $(TEST_DIR) -v -m smoke

# =============================================================================
# TEST REPORTS
# =============================================================================

.PHONY: coverage-report
coverage-report: ## Generate and open coverage report
	$(PYTEST) --cov=src --cov=infrastructure --cov-report=html:$(COVERAGE_DIR)
	@echo "Coverage report generated in $(COVERAGE_DIR)/index.html"

.PHONY: test-report
test-report: ## Generate test report
	$(PYTEST) $(TEST_DIR) --junitxml=$(TEST_RESULTS) --html=test-report.html

.PHONY: performance-report
performance-report: ## Generate performance test report
	$(PYTEST) $(TEST_DIR)/performance/ --junitxml=$(PERFORMANCE_RESULTS) -v

# =============================================================================
# CODE QUALITY
# =============================================================================

.PHONY: lint
lint: ## Run linting checks
	flake8 src/ infrastructure/ tests/
	black --check src/ infrastructure/ tests/
	mypy src/ infrastructure/

.PHONY: format
format: ## Format code with black
	black src/ infrastructure/ tests/

.PHONY: lint-fix
lint-fix: ## Fix linting issues automatically
	black src/ infrastructure/ tests/
	isort src/ infrastructure/ tests/

# =============================================================================
# INFRASTRUCTURE COMMANDS
# =============================================================================

.PHONY: synth
synth: ## Synthesize CDK app
	cdk synth

.PHONY: deploy
deploy: ## Deploy infrastructure
	cdk deploy --all

.PHONY: destroy
destroy: ## Destroy infrastructure
	cdk destroy --all

.PHONY: diff
diff: ## Show infrastructure changes
	cdk diff

# =============================================================================
# DOCKER COMMANDS
# =============================================================================

.PHONY: docker-build
docker-build: ## Build Docker image
	$(DOCKER) build -t $(PROJECT_NAME):latest .

.PHONY: docker-run
docker-run: ## Run Docker container
	$(DOCKER) run -p 8000:8000 $(PROJECT_NAME):latest

.PHONY: docker-test
docker-test: ## Run tests in Docker container
	$(DOCKER) run $(PROJECT_NAME):latest make test

.PHONY: docker-compose-up
docker-compose-up: ## Start services with Docker Compose
	$(DOCKER_COMPOSE) up -d

.PHONY: docker-compose-down
docker-compose-down: ## Stop services with Docker Compose
	$(DOCKER_COMPOSE) down

# =============================================================================
# CI/CD COMMANDS
# =============================================================================

.PHONY: ci-test
ci-test: ## Run tests for CI/CD pipeline
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov pytest-mock moto psutil
	$(PYTEST) $(TEST_DIR)/unit/ --cov=src --cov-report=xml
	$(PYTEST) $(TEST_DIR)/integration/ -m "not slow"
	$(PYTEST) $(TEST_DIR)/performance/ --junitxml=$(PERFORMANCE_RESULTS)

.PHONY: ci-lint
ci-lint: ## Run linting for CI/CD pipeline
	$(PIP) install black flake8 mypy
	flake8 src/ infrastructure/ tests/
	black --check src/ infrastructure/ tests/
	mypy src/ infrastructure/

.PHONY: ci-security
ci-security: ## Run security checks
	$(PIP) install bandit safety
	bandit -r src/ infrastructure/
	safety check

# =============================================================================
# DEVELOPMENT WORKFLOW
# =============================================================================

.PHONY: dev-setup
dev-setup: ## Setup development environment
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	pre-commit install

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

.PHONY: validate
validate: ## Validate code quality and tests
	make lint
	make test-fast
	make test-coverage

.PHONY: full-test
full-test: ## Run complete test suite
	make test-coverage
	make test-performance
	make test-e2e

# =============================================================================
# UTILITY COMMANDS
# =============================================================================

.PHONY: generate-docs
generate-docs: ## Generate documentation
	sphinx-build -b html docs/ docs/_build/html

.PHONY: serve-docs
serve-docs: ## Serve documentation locally
	cd docs/_build/html && python -m http.server 8000

.PHONY: check-deps
check-deps: ## Check for outdated dependencies
	$(PIP) list --outdated

.PHONY: update-deps
update-deps: ## Update dependencies
	$(PIP) install --upgrade -r requirements.txt

.PHONY: backup
backup: ## Create backup of important files
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz \
		src/ infrastructure/ tests/ requirements.txt README.md

# =============================================================================
# MONITORING AND LOGS
# =============================================================================

.PHONY: logs
logs: ## View application logs
	$(DOCKER_COMPOSE) logs -f

.PHONY: monitor
monitor: ## Monitor system resources
	htop

.PHONY: health-check
health-check: ## Run health checks
	curl -f http://localhost:8000/health || echo "Service not running"

# =============================================================================
# CLEANUP COMMANDS
# =============================================================================

.PHONY: clean-all
clean-all: ## Clean everything including Docker
	make clean
	$(DOCKER) system prune -f
	$(DOCKER) volume prune -f

.PHONY: reset
reset: ## Reset development environment
	make clean-all
	make install
	make dev-setup

# =============================================================================
# DEPLOYMENT COMMANDS
# =============================================================================

.PHONY: deploy-dev
deploy-dev: ## Deploy to development environment
	ENV_NAME=development make deploy

.PHONY: deploy-staging
deploy-staging: ## Deploy to staging environment
	ENV_NAME=staging make deploy

.PHONY: deploy-prod
deploy-prod: ## Deploy to production environment
	ENV_NAME=production make deploy

# =============================================================================
# TROUBLESHOOTING
# =============================================================================

.PHONY: debug
debug: ## Debug mode with verbose output
	$(PYTEST) $(TEST_DIR) -v -s --tb=long --maxfail=1

.PHONY: test-memory
test-memory: ## Test memory usage
	$(PYTEST) $(TEST_DIR)/performance/ -v -s -k "memory"

.PHONY: test-slow
test-slow: ## Run only slow tests
	$(PYTEST) $(TEST_DIR) -v -m slow

# =============================================================================
# DEFAULT TARGET
# =============================================================================

.DEFAULT_GOAL := help
