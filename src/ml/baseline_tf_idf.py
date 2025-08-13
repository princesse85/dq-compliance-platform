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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create analytics directory - try multiple paths
analytics_paths = [
    pathlib.Path("analytics/models/baseline"),
    pathlib.Path("../../analytics/models/baseline"),
    pathlib.Path("../../../analytics/models/baseline")
]

ANALYTICS_DIR = None
for path in analytics_paths:
    try:
        path.mkdir(parents=True, exist_ok=True)
        ANALYTICS_DIR = path
        break
    except:
        continue

if ANALYTICS_DIR is None:
    ANALYTICS_DIR = pathlib.Path("analytics/models/baseline")
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)


def load_split(split):
    """Load train/valid/test split data."""
    # Try different possible paths
    paths_to_try = [
        f"src/data/text_corpus/{split}.csv",
        f"../data/text_corpus/{split}.csv",
        f"../../src/data/text_corpus/{split}.csv"
    ]
    
    for path in paths_to_try:
        if pathlib.Path(path).exists():
            df = pd.read_csv(path)
            return df["text"].tolist(), df["label"].tolist()
    
    raise FileNotFoundError(f"Could not find {split}.csv in any of the expected locations: {paths_to_try}")


if __name__ == "__main__":
    logger.info("Starting baseline TF-IDF + Logistic Regression training...")

    # Load data
    X_train, y_train = load_split("train")
    X_valid, y_valid = load_split("valid")
    X_test, y_test = load_split("test")

    logger.info(f"Loaded {len(X_train)} training samples, {len(X_valid)} validation samples, {len(X_test)} test samples")

    # Encode labels
    le = LabelEncoder()
    le.fit(y_train + y_valid + y_test)
    classes = list(le.classes_)

    logger.info(f"Classes: {classes}")

    # Create pipeline
    pipe = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.9)),
            ("clf", LogisticRegression(max_iter=200, random_state=42)),
        ]
    )

    # Train model
    logger.info("Training model...")
    pipe.fit(X_train, le.transform(y_train))

    # Evaluate on test set
    logger.info("Evaluating model...")
    y_pred = pipe.predict(X_test)
    rep = classification_report(le.transform(y_test), y_pred, target_names=classes, output_dict=True)
    cm = confusion_matrix(le.transform(y_test), y_pred)

    # Save artifacts
    dump(pipe, ANALYTICS_DIR / "model.joblib")
    with open(ANALYTICS_DIR / "metrics.json", "w") as f:
        json.dump(rep, f, indent=2)
    np.savetxt(ANALYTICS_DIR / "confusion_matrix.csv", cm, delimiter=",", fmt="%d")

    logger.info(f"Model saved to {ANALYTICS_DIR}")
    logger.info(f"F1 Score (weighted): {rep['weighted avg']['f1-score']:.4f}")
    logger.info("Baseline training completed successfully!")
