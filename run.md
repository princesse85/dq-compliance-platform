# How to Run the DQ Compliance Platform Locally

This guide provides a streamlined, step-by-step process for setting up and running the DQ Compliance Platform on your local machine for development purposes.

## 1. Clone the Repository

First, clone the project repository from GitHub:

```bash
git clone https://github.com/princesse85/dq-compliance-platform.git
cd dq-compliance-platform
```

## 2. Set Up the Environment and Install Dependencies

Next, set up a Python virtual environment and install the required packages from `requirements.txt`.

### For Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### For macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Configure the Environment

Run the `configure_env.py` script to create the necessary configuration files and directories. This script will generate a `.env` file and a `.streamlit/config.toml` file.

```bash
python scripts/configure_env.py
```

**Note:** This script may check for AWS credentials, but they are not required for local development. You can ignore any warnings about AWS.

## 4. Generate Data and Train Models (or Use Existing Data)

The `generate_data_and_train.py` script creates synthetic data and then trains the machine learning models. This process can be very time-consuming.

**To run the full data generation and training process (slow):**

```bash
python scripts/generate_data_and_train.py
```

**To skip the lengthy data generation and training process (fast):**

For a faster startup, you can use the sample data that is already included in the repository. The Streamlit application is configured to use local data by default (`USE_LOCAL_DATA=true` in the `.env` file), so you can proceed to the next step without running the script above. The application will use the data in the `assets` and `src/data` directories.

## 5. Run the Streamlit Application

Once your environment is configured, you can run the Streamlit application:

```bash
streamlit run streamlit_app.py
```

The application should now be running and accessible in your web browser at `http://localhost:8501`.
