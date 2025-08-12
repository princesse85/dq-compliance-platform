import json
import pathlib
import numpy as np
from joblib import load

MODEL_DIR = pathlib.Path('analytics/models/baseline')

if __name__ == '__main__':
    pipe = load(MODEL_DIR / 'model.joblib')
    clf = pipe.named_steps['clf']
    vec = pipe.named_steps['tfidf']
    feature_names = np.array(vec.get_feature_names_out())
    coefs = clf.coef_  # shape [n_classes, n_features]

    topn = 15
    out = {}
    for i, cls in enumerate(clf.classes_):
        idx = np.argsort(coefs[i])[::-1][:topn]
        out[str(cls)] = feature_names[idx].tolist()

    with open(MODEL_DIR / 'global_top_words.json', 'w') as f:
        json.dump(out, f, indent=2)
    print('Saved global_top_words.json')
