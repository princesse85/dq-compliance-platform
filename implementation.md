# DQ Compliance Platform: End-to-End Workflow

The application is a self-contained **Streamlit dashboard** that allows users to analyze legal documents for compliance risks. Here’s how it works:



### 1. Dashboard Initialization
*   When the Streamlit application is started, the main dashboard code in `src/dashboard/main.py` is executed.
*   The dashboard initializes a `RealMLPredictor` class from `src/dashboard/real_ml_utils.py`. This class is responsible for loading the trained machine learning model.
*   The predictor loads a baseline model from the file `analytics/models/baseline/model.joblib`. This model is a trained TF-IDF logistic regression model.

### 2. Data Loading and Visualization
*   The dashboard loads compliance data to populate the charts and tables in the "Executive Dashboard" and "Risk Analytics" tabs.
*   It attempts to load real data from `src/data/text_corpus/train.csv`. If this file is not available, it generates mock data for demonstration purposes.

### 3. Document Analysis (User Interaction)
*   The core feature is in the **"Document Intelligence"** tab. Here, a user can upload a document (PDF or TXT file).
*   The dashboard reads the content of the uploaded file. If it's a PDF, it uses the `PyMuPDF` library to extract the text.
*   The extracted text is then passed to the `predict_risk` method of the loaded `RealMLPredictor`.
*   The `predict_risk` method uses the loaded baseline model to predict a risk level (`HighRisk`, `MediumRisk`, or `LowRisk`) and a confidence score.

### 4. Displaying Results
*   The prediction results are used to generate a full analysis, including:
    *   A compliance score.
    *   The predicted risk level.
    *   Key risks identified (based on the prediction).
    *   Recommendations for what to do next.
    *   A basic sentiment analysis of the document.
*   This analysis is then displayed to the user on the dashboard.

### Alternative Implementation (`lambda_app`)

It's worth noting that the project also contains a directory named `lambda_app`, which defines a server-based API using FastAPI. This API is designed to be deployed as an AWS Lambda function and provides a `/predict` endpoint. However, based on my analysis, the Streamlit dashboard does **not** use this API. Instead, it loads and runs the model in the same process as the dashboard itself. The `lambda_app` is likely an alternative implementation for a production environment where the model is served via an API, but it is not what is currently wired up to the dashboard.