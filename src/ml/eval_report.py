import json
import pathlib
from sklearn.metrics import roc_auc_score
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

OUT = pathlib.Path("analytics/models")

if __name__ == "__main__":
    # Load metrics from both models
    baseline = json.load(open(OUT / "baseline/metrics.json"))
    transformer = json.load(open(OUT / "transformer/metrics.json"))

    # Create overview comparison
    overview = {
        "baseline": {
            "f1_weighted": baseline["weighted avg"]["f1-score"],
            "precision_weighted": baseline["weighted avg"]["precision"],
            "recall_weighted": baseline["weighted avg"]["recall"],
        },
        "transformer": {"f1_weighted": transformer.get("eval_f1_weighted"), "eval_loss": transformer.get("eval_loss")},
    }

    # Save overview
    json.dump(overview, open(OUT / "metrics_overview.json", "w"), indent=2)

    # Print comparison
    logger.info(r"Model Performance Comparison:")
    logger.info("=" * 40)
    logger.info(r"Baseline F1 (weighted): {overview['baseline']['f1_weighted']:.4f}")
    logger.info(r"Transformer F1 (weighted): {overview['transformer']['f1_weighted']:.4f}")
    logger.info(r"Improvement: {overview['transformer']['f1_weighted'] - overview['baseline']['f1_weighted']:.4f}")
    logger.info(r"\nDetailed metrics saved to analytics/models/metrics_overview.json")
