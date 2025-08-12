import os
import json
import pathlib
import random
import pandas as pd
from joblib import load
from lime.lime_text import LimeTextExplainer
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

OUT_DIR = pathlib.Path('analytics/models/explanations')
OUT_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)

# Common loader for samples
TEST = pd.read_csv('data/text_corpus/test.csv')
LABELS = sorted(TEST['label'].unique())

def explain_baseline(n_per_label=5):
    """Generate LIME explanations for baseline model."""
    pipe: Pipeline = load('analytics/models/baseline/model.joblib')
    explainer = LimeTextExplainer(class_names=LABELS)
    chosen = []
    
    for lab in LABELS:
        subset = TEST[TEST['label'] == lab].sample(min(n_per_label, TEST[TEST['label'] == lab].shape[0]))
        for _, row in subset.iterrows():
            exp = explainer.explain_instance(row['text'], pipe.predict_proba, num_features=10)
            fname = OUT_DIR / f"baseline_{lab}_{len(chosen)}.html"
            exp.save_to_file(str(fname))
            chosen.append(fname.name)
    
    with open(OUT_DIR / 'baseline_index.json', 'w') as f:
        json.dump([str(x) for x in chosen], f, indent=2)

def explain_transformer(model_dir='analytics/models/transformer/hf_model', n_per_label=5):
    """Generate LIME explanations for transformer model."""
    tok = AutoTokenizer.from_pretrained(model_dir)
    mdl = AutoModelForSequenceClassification.from_pretrained(model_dir)
    pipe = TextClassificationPipeline(model=mdl, tokenizer=tok, return_all_scores=True)
    class_names = LABELS
    explainer = LimeTextExplainer(class_names=class_names)

    chosen = []
    for lab in class_names:
        subset = TEST[TEST['label'] == lab].sample(min(n_per_label, TEST[TEST['label'] == lab].shape[0]))
        for _, row in subset.iterrows():
            # LIME needs a proba function: convert list-of-dicts → ordered proba array
            def proba_fn(texts):
                out = []
                for t in texts:
                    scores = pipe(t)[0]  # list of {label, score}
                    # Ensure order stable across labels
                    m = {d['label']: d['score'] for d in scores}
                    out.append([m.get(f'LABEL_{i}', 0.0) for i in range(len(class_names))])
                return out
            
            exp = explainer.explain_instance(row['text'], proba_fn, num_features=10)
            fname = OUT_DIR / f"transformer_{lab}_{len(chosen)}.html"
            exp.save_to_file(str(fname))
            chosen.append(fname.name)
    
    with open(OUT_DIR / 'transformer_index.json', 'w') as f:
        json.dump([str(x) for x in chosen], f, indent=2)

if __name__ == '__main__':
    explain_baseline()
    explain_transformer()
    print('Saved LIME explanations to analytics/models/explanations')
