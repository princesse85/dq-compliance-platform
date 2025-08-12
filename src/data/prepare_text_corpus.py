import csv
import random
import pathlib
from typing import List, Tuple
from src.utils.logging_config import get_logger

logger = get_logger(__name__)
random.seed(42)

def read_rows(path: str) -> List[Tuple[str, str]]:
    """Read CSV file and return list of (text, label) tuples."""
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            txt = row['text'].strip()
            lab = row['label'].strip()
            if txt and lab:
                rows.append((txt, lab))
    return rows

def create_splits_from_existing():
    """Create train/valid/test splits from existing CSV files."""
    base = pathlib.Path("data/text_corpus")
    base.mkdir(parents=True, exist_ok=True)
    
    # Check if we have individual files already
    if (base / "train.csv").exists() and (base / "valid.csv").exists() and (base / "test.csv").exists():
        logger.info("Train/valid/test splits already exist.")
        return
    
    # If we have a single source file, create splits
    src = base / "all.csv"
    if src.exists():
        rows = read_rows(str(src))
        random.shuffle(rows)
        n = len(rows)
        n_train, n_valid = int(0.7 * n), int(0.15 * n)
        
        splits = {
            'train.csv': rows[:n_train],
            'valid.csv': rows[n_train:n_train + n_valid],
            'test.csv': rows[n_train + n_valid:]
        }
        
        for name, items in splits.items():
            with open(base / name, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['text', 'label'])
                w.writerows(items)
        
        logger.info(f"Split sizes: {dict((k, len(v)) for k, v in splits.items())}")
    else:
        logger.info("No source file found. Using existing synthetic data.")

if __name__ == "__main__":
    create_splits_from_existing()
