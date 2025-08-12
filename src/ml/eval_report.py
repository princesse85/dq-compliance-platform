import json
import pathlib
from sklearn.metrics import roc_auc_score

OUT = pathlib.Path('analytics/models')

if __name__ == '__main__':
    # Load metrics from both models
    baseline = json.load(open(OUT / 'baseline/metrics.json'))
    transformer = json.load(open(OUT / 'transformer/metrics.json'))
    
    # Create overview comparison
    overview = {
        'baseline': {
            'f1_weighted': baseline['weighted avg']['f1-score'],
            'precision_weighted': baseline['weighted avg']['precision'],
            'recall_weighted': baseline['weighted avg']['recall']
        },
        'transformer': {
            'f1_weighted': transformer.get('eval_f1_weighted'),
            'eval_loss': transformer.get('eval_loss')
        }
    }
    
    # Save overview
    json.dump(overview, open(OUT / 'metrics_overview.json', 'w'), indent=2)
    
    # Print comparison
    print("Model Performance Comparison:")
    print("=" * 40)
    print(f"Baseline F1 (weighted): {overview['baseline']['f1_weighted']:.4f}")
    print(f"Transformer F1 (weighted): {overview['transformer']['f1_weighted']:.4f}")
    print(f"Improvement: {overview['transformer']['f1_weighted'] - overview['baseline']['f1_weighted']:.4f}")
    print("\nDetailed metrics saved to analytics/models/metrics_overview.json")
