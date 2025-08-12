# Multi-stage build for Enterprise Data Quality & Compliance Platform
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /var/log/enterprise_dq /app/logs

# Set ownership
RUN chown -R appuser:appuser /app /var/log/enterprise_dq

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "app.py"]

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    safety \
    bandit

# Development command
CMD ["python", "-m", "pytest", "tests/", "-v"]

# Production stage
FROM base as production

# Copy production configuration
COPY config/production.py /app/config/

# Set production environment
ENV ENV_NAME=production \
    PYTHONPATH=/app

# Production command
CMD ["python", "app.py"]

# Lambda stage for serverless deployment
FROM public.ecr.aws/lambda/python:3.9 as lambda

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ${LAMBDA_TASK_ROOT}/src/
COPY lambda_app/ ${LAMBDA_TASK_ROOT}/

# Set Lambda handler
CMD ["lambda_app.handler"]
