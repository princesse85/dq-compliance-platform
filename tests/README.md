# Data Quality Compliance Platform - Test Suite

This directory contains comprehensive unit and integration tests for the Data Quality Compliance Platform.

## Test Structure

```
tests/
├── conftest.py                 # Test fixtures and configuration
├── unit/                       # Unit tests for individual components
│   ├── test_infrastructure.py  # CDK stacks and infrastructure tests
│   ├── test_data_quality.py    # Data quality assessment tests
│   ├── test_ml_components.py   # ML model and training tests
│   └── test_etl_pipelines.py   # ETL pipeline tests
├── integration/                # Integration tests
│   ├── test_end_to_end.py      # End-to-end workflow tests
│   └── test_aws_integration.py # AWS service integration tests
└── performance/                # Performance and load tests
    └── test_performance.py     # Performance benchmarks
```

## Test Categories

### Unit Tests (`tests/unit/`)

- **Infrastructure Tests**: CDK stack creation, resource validation, security configurations
- **Data Quality Tests**: Quality assessment, validation suites, synthetic data generation
- **ML Component Tests**: Model training, evaluation, feature extraction
- **ETL Pipeline Tests**: Data transformation, validation, error handling

### Integration Tests (`tests/integration/`)

- **End-to-End Tests**: Complete workflow validation from data ingestion to insights
- **AWS Integration Tests**: S3, Lambda, SQS, SNS, CloudWatch service interactions

### Performance Tests (`tests/performance/`)

- **Scalability Tests**: Performance with different dataset sizes
- **Load Tests**: Concurrent processing and throughput validation
- **Memory Tests**: Memory efficiency and resource usage

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements.txt

# Install additional test packages
pip install pytest pytest-cov pytest-mock moto psutil
```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Running Specific Test Categories

```bash
# Run only unit tests
pytest tests/unit/ -m unit

# Run only integration tests
pytest tests/integration/ -m integration

# Run only performance tests
pytest tests/performance/ -m performance

# Run AWS integration tests
pytest tests/integration/test_aws_integration.py -m aws

# Run end-to-end tests
pytest tests/integration/test_end_to_end.py -m slow
```

### Running Specific Test Files

```bash
# Run infrastructure tests
pytest tests/unit/test_infrastructure.py

# Run data quality tests
pytest tests/unit/test_data_quality.py

# Run ML component tests
pytest tests/unit/test_ml_components.py

# Run ETL pipeline tests
pytest tests/unit/test_etl_pipelines.py
```

### Test Markers

- `@pytest.mark.unit`: Unit tests for individual components
- `@pytest.mark.integration`: Integration tests for component interactions
- `@pytest.mark.aws`: Tests requiring AWS services (mocked)
- `@pytest.mark.slow`: Slow-running tests (end-to-end, performance)
- `@pytest.mark.performance`: Performance and load tests
- `@pytest.mark.smoke`: Quick smoke tests for basic functionality

### Parallel Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

## Test Configuration

### Environment Variables

Tests use the following environment variables:

- `ENV_NAME=test`: Test environment name
- `PROJECT_PREFIX=test`: Test project prefix
- `AWS_DEFAULT_REGION=us-east-1`: AWS region for tests
- `PYTHONPATH=.`: Python path for imports

### Coverage Requirements

- Minimum coverage: 80%
- Coverage reports: HTML, XML, and terminal output
- Coverage includes: `src/` and `infrastructure/` directories

## Test Data

### Sample Data Fixtures

- `sample_contracts_data`: Sample contract data for testing
- `sample_text_data`: Sample text data for ML testing
- `problematic_data`: Data with quality issues for testing
- `large_dataset`: Large dataset for performance testing

### Mock Services

- **AWS Services**: S3, Lambda, SQS, SNS, CloudWatch (using moto)
- **ML Models**: Mocked transformer models and training
- **External APIs**: Mocked API responses

## Performance Benchmarks

### Quality Assessment Performance

- **Small datasets** (100-1,000 records): < 60 seconds
- **Medium datasets** (1,000-10,000 records): < 120 seconds
- **Large datasets** (10,000+ records): < 300 seconds

### ETL Pipeline Performance

- **Processing time**: < 120 seconds for 50,000 records
- **Memory usage**: < 4GB peak usage
- **Throughput**: > 100 records/second

### ML Training Performance

- **Training time**: < 300 seconds for 10,000 records
- **Prediction time**: < 10 seconds for 1,000 records
- **Memory usage**: < 2GB during training

## Test Reports

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Performance Reports

```bash
# Run performance tests with detailed output
pytest tests/performance/ -v -s

# Generate performance report
pytest tests/performance/ --junitxml=performance-results.xml
```

### Test Results

```bash
# Generate JUnit XML report
pytest --junitxml=test-results.xml

# Generate HTML report (requires pytest-html)
pip install pytest-html
pytest --html=test-report.html
```

## Continuous Integration

### GitHub Actions

Tests are automatically run on:

- Pull requests
- Push to main branch
- Scheduled runs (daily)

### Test Commands for CI

```bash
# Install dependencies
pip install -r requirements.txt

# Run unit tests
pytest tests/unit/ --cov=src --cov-report=xml

# Run integration tests
pytest tests/integration/ -m "not slow"

# Run performance tests (nightly)
pytest tests/performance/ --junitxml=performance-results.xml
```

## Troubleshooting

### Common Issues

1. **Import Errors**

   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH=.
   pytest
   ```

2. **AWS Credentials**

   ```bash
   # Tests use mocked AWS services, no real credentials needed
   # If you see credential errors, check moto installation
   pip install moto
   ```

3. **Memory Issues**

   ```bash
   # Reduce dataset sizes for performance tests
   pytest tests/performance/ -k "not large_dataset"
   ```

4. **Slow Tests**

   ```bash
   # Skip slow tests
   pytest -m "not slow"

   # Run only fast tests
   pytest -m "unit or integration"
   ```

### Debug Mode

```bash
# Run tests with debug output
pytest -v -s --tb=long

# Run specific test with debug
pytest tests/unit/test_data_quality.py::TestDataQualityAssessment::test_completeness_check -v -s
```

## Adding New Tests

### Unit Test Template

```python
import pytest
from unittest.mock import Mock, patch

class TestNewComponent:
    """Unit tests for NewComponent"""

    def setup_method(self):
        """Setup test data"""
        self.component = NewComponent()

    def test_basic_functionality(self):
        """Test basic functionality"""
        result = self.component.process(data)
        assert result is not None
        assert result['status'] == 'success'

    def test_error_handling(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            self.component.process(invalid_data)
```

### Integration Test Template

```python
import pytest

class TestNewIntegration:
    """Integration tests for new workflow"""

    def test_end_to_end_workflow(self):
        """Test complete workflow"""
        # Setup
        data = self.generate_test_data()

        # Execute
        result = self.run_workflow(data)

        # Verify
        assert result['status'] == 'success'
        assert result['quality_score'] > 0.8
```

### Performance Test Template

```python
import pytest
import time

class TestNewPerformance:
    """Performance tests for new component"""

    @pytest.mark.performance
    def test_scaling_performance(self):
        """Test performance scaling"""
        dataset_sizes = [100, 1000, 10000]

        for size in dataset_sizes:
            data = self.generate_dataset(size)

            start_time = time.time()
            result = self.component.process(data)
            execution_time = time.time() - start_time

            assert execution_time < 60, f"Too slow: {execution_time:.2f}s"
```

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Mock External Dependencies**: Use mocks for AWS services, APIs, and external systems
3. **Use Fixtures**: Leverage pytest fixtures for common test data and setup
4. **Meaningful Assertions**: Test specific behaviors, not just that code runs
5. **Performance Thresholds**: Set realistic performance expectations
6. **Error Scenarios**: Test both success and failure cases
7. **Documentation**: Document complex test scenarios and expected behaviors

## Contributing

When adding new tests:

1. Follow the existing test structure and naming conventions
2. Add appropriate markers for test categorization
3. Include both positive and negative test cases
4. Add performance tests for new components
5. Update this README if adding new test categories
6. Ensure tests pass in CI environment


