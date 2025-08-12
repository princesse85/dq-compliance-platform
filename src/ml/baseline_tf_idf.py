import os
import json
import pathlib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from joblib import dump
import mlflow
import sys

sys.path.append("src/ml")
from mlflow_utils import init_mlflow
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

ANALYTICS_DIR = pathlib.Path("analytics/models/baseline")
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)


def load_split(split):
    """Load train/valid/test split data."""
    df = pd.read_csv(f"data/text_corpus/{split}.csv")
    return df["text"].tolist(), df["label"].tolist()


if __name__ == "__main__":
    mlflow = init_mlflow("baseline_tfidf_lr")

    # Load data
    X_train, y_train = load_split("train")
    X_valid, y_valid = load_split("valid")
    X_test, y_test = load_split("test")

    # Encode labels
    le = LabelEncoder()
    le.fit(y_train + y_valid + y_test)
    classes = list(le.classes_)

    # Create pipeline
    pipe = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.9)),
            ("clf", LogisticRegression(max_iter=200, random_state=42)),
        ]
    )

    # Train model
    pipe.fit(X_train, le.transform(y_train))

    # Evaluate on test set
    y_pred = pipe.predict(X_test)
    rep = classification_report(le.transform(y_test), y_pred, target_names=classes, output_dict=True)
    cm = confusion_matrix(le.transform(y_test), y_pred)

    # Save artifacts
    dump(pipe, ANALYTICS_DIR / "model.joblib")
    with open(ANALYTICS_DIR / "metrics.json", "w") as f:
        json.dump(rep, f, indent=2)
    np.savetxt(ANALYTICS_DIR / "confusion_matrix.csv", cm, delimiter=",", fmt="%d")

    # Log to MLflow
    mlflow.log_metric("f1_weighted", rep["weighted avg"]["f1-score"])
    for lbl in classes:
        mlflow.log_metric(f"f1_{lbl}", rep[lbl]["f1-score"])
    mlflow.log_artifact(str(ANALYTICS_DIR / "metrics.json"))
    mlflow.log_artifact(str(ANALYTICS_DIR / "confusion_matrix.csv"))

    logger.info("Baseline done. F1(weighted)=", round(rep["weighted avg"]["f1-score"], 4))
