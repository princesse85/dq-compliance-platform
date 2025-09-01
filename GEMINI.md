# GEMINI Code Assistant Context

This document provides context for the Gemini AI assistant to understand the DQ Compliance Platform project.

## Project Overview

The DQ Compliance Platform is an enterprise-grade solution designed to monitor and ensure data quality compliance across organizational datasets. Built with a modern microservices architecture, the platform combines automated data validation, machine learning-powered anomaly detection, and real-time monitoring capabilities to provide comprehensive data governance.

The platform primarily targets contract management systems but can be adapted for various compliance domains. It features a Streamlit-based dashboard for user interaction, automated data quality checks using Great Expectations, and transformer-based models for advanced document analysis.

**Key Technologies:**

- **Backend:** Python, Flask (inferred from `lambda_app`)
- **Frontend:** Streamlit
- **Infrastructure:** AWS CDK (Cloud Development Kit)
- **Data Quality:** Great Expectations
- **Machine Learning:** Hugging Face Transformers, scikit-learn

**Architecture:**

The platform follows a modular, cloud-native architecture with the following key layers:

1.  **Presentation Layer**: Streamlit dashboard for user interaction and visualization
2.  **Application Layer**: Python services handling business logic, data processing, and ML inference
3.  **Data Layer**: Structured and unstructured data storage with validation mechanisms
4.  **Infrastructure Layer**: AWS-based cloud infrastructure managed by AWS CDK

## Building and Running

**TODO:** The following commands are inferred from the project structure and `README.md`. Please verify and update them.

**Local Development:**

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```
2.  **Configure environment variables:**
    - Copy `.streamlit/secrets.toml.template` to `.streamlit/secrets.toml` and update the values.
    - Copy `config/environment.example` to `config/environment` and update the values.
3.  **Run the dashboard:**
    ```bash
    streamlit run streamlit_app.py
    ```

**Cloud Deployment (AWS):**

1.  **Install AWS CDK:**
    ```bash
    npm install -g aws-cdk
    ```
2.  **Bootstrap CDK:**
    ```bash
    cdk bootstrap
    ```
3.  **Deploy stacks:**
    ```bash
    cdk deploy --all
    ```

## Development Conventions

- **Code Style:** The project appears to follow the PEP 8 style guide for Python code.
- **Testing:** The project uses `pytest` for testing. Tests are located in the `tests` directory, with subdirectories for unit, integration, and performance tests.
- **Infrastructure as Code:** Infrastructure is managed using AWS CDK. Stack definitions are located in the `infrastructure` directory.
- **Machine Learning:** The project uses MLflow for experiment tracking. The `mlruns` directory contains the MLflow tracking data.
- **Contributing:** The `CONTRIBUTING.md` file provides guidelines for contributing to the project.
