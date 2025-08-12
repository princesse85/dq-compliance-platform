import os
import json
import pathlib
import numpy as np
import pandas as pd
from datasets import Dataset
from evaluate import load
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from sklearn.preprocessing import LabelEncoder
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create analytics directory
ANALYTICS_DIR = pathlib.Path("analytics/models/transformer")
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = os.getenv("MODEL_NAME", "distilbert-base-uncased")
EPOCHS = float(os.getenv("EPOCHS", "2"))
BATCH = int(os.getenv("BATCH", "8"))
LR = float(os.getenv("LR", "5e-5"))


def load_df(split):
    """Load dataset split as DataFrame."""
    return pd.read_csv(f"src/data/text_corpus/{split}.csv")


if __name__ == "__main__":
    logger.info(f"Starting transformer training with {MODEL_NAME}...")

    # Load data
    train_df = load_df("train")
    valid_df = load_df("valid")
    test_df = load_df("test")

    logger.info(f"Loaded {len(train_df)} training samples, {len(valid_df)} validation samples, {len(test_df)} test samples")

    # Encode labels
    le = LabelEncoder()
    le.fit(train_df["label"].tolist() + valid_df["label"].tolist() + test_df["label"].tolist())

    logger.info(f"Classes: {list(le.classes_)}")

    # Initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tok(batch):
        """Tokenize batch of texts."""
        return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=256)

    def to_ds(df):
        """Convert DataFrame to HuggingFace Dataset."""
        return Dataset.from_pandas(
            pd.DataFrame({"text": df["text"].tolist(), "label": le.transform(df["label"].tolist())})
        )

    # Prepare datasets
    logger.info("Preparing datasets...")
    train_ds = to_ds(train_df).map(tok, batched=True)
    valid_ds = to_ds(valid_df).map(tok, batched=True)
    test_ds = to_ds(test_df).map(tok, batched=True)

    # Initialize model
    logger.info("Initializing model...")
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=len(le.classes_))

    # Setup metrics
    metric = load("f1")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        return {"f1_weighted": metric.compute(predictions=preds, references=labels, average="weighted")["f1"]}

    # Training arguments
    args = TrainingArguments(
        output_dir=str(ANALYTICS_DIR / "checkpoints"),
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=LR,
        per_device_train_batch_size=BATCH,
        per_device_eval_batch_size=BATCH,
        num_train_epochs=EPOCHS,
        weight_decay=0.01,
        logging_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="f1_weighted",
        save_total_limit=2,
    )

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    # Train model
    logger.info("Starting training...")
    trainer.train()

    # Evaluate on test set
    logger.info("Evaluating on test set...")
    results = trainer.evaluate(test_ds)
    
    # Save model and results
    trainer.save_model(str(ANALYTICS_DIR / "final_model"))
    tokenizer.save_pretrained(str(ANALYTICS_DIR / "final_model"))
    
    with open(ANALYTICS_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Model saved to {ANALYTICS_DIR}")
    logger.info(f"Test F1 Score: {results.get('eval_f1_weighted', 0):.4f}")
    logger.info("Transformer training completed successfully!")
