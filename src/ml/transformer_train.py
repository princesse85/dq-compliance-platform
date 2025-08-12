import os
import json
import pathlib
import numpy as np
import pandas as pd
from datasets import Dataset, load_metric
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from sklearn.preprocessing import LabelEncoder
import mlflow
import sys
sys.path.append('src/ml')
from mlflow_utils import init_mlflow
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

ANALYTICS_DIR = pathlib.Path('analytics/models/transformer')
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = os.getenv('MODEL_NAME', 'distilbert-base-uncased')
EPOCHS = float(os.getenv('EPOCHS', '2'))
BATCH = int(os.getenv('BATCH', '8'))
LR = float(os.getenv('LR', '5e-5'))

def load_df(split):
    """Load dataset split as DataFrame."""
    return pd.read_csv(f'data/text_corpus/{split}.csv')

if __name__ == '__main__':
    mlflow = init_mlflow('transformer_' + MODEL_NAME)

    # Load data
    train_df = load_df('train')
    valid_df = load_df('valid')
    test_df = load_df('test')
    
    # Encode labels
    le = LabelEncoder()
    le.fit(train_df['label'].tolist() + valid_df['label'].tolist() + test_df['label'].tolist())

    # Initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tok(batch):
        """Tokenize batch of texts."""
        return tokenizer(batch['text'], truncation=True, padding='max_length', max_length=256)

    def to_ds(df):
        """Convert DataFrame to HuggingFace Dataset."""
        return Dataset.from_pandas(pd.DataFrame({
            'text': df['text'].tolist(),
            'label': le.transform(df['label'].tolist())
        }))

    # Prepare datasets
    train_ds = to_ds(train_df).map(tok, batched=True)
    valid_ds = to_ds(valid_df).map(tok, batched=True)
    test_ds = to_ds(test_df).map(tok, batched=True)

    # Initialize model
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=len(le.classes_))

    # Setup metrics
    metric = load_metric('f1')
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        return {'f1_weighted': metric.compute(predictions=preds, references=labels, average='weighted')['f1']}

    # Training arguments
    args = TrainingArguments(
        output_dir='analytics/tmp',
        evaluation_strategy='epoch',
        save_strategy='epoch',
        learning_rate=LR,
        per_device_train_batch_size=BATCH,
        per_device_eval_batch_size=BATCH,
        num_train_epochs=EPOCHS,
        weight_decay=0.01,
        logging_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model='f1_weighted',
        save_total_limit=2
    )

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    # Train model
    trainer.train()
    
    # Evaluate on test set
    eval_metrics = trainer.evaluate(test_ds)

    # Save artifacts
    with open(ANALYTICS_DIR / 'metrics.json', 'w') as f:
        json.dump(eval_metrics, f, indent=2)
    trainer.save_model(ANALYTICS_DIR / 'hf_model')

    # Log to MLflow
    mlflow.log_metric('f1_weighted', float(eval_metrics.get('eval_f1_weighted', 0)))
    mlflow.log_artifact(str(ANALYTICS_DIR / 'metrics.json'))

    logger.info('Transformer done. F1(weighted)=', round(float(eval_metrics.get('eval_f1_weighted', 0)), 4))
