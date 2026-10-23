from __future__ import annotations

import json

from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

from app.services.ml.recommendation_engine import MODEL, _training_samples


def evaluate_model() -> dict[str, float]:
    samples, labels = _training_samples()
    probabilities = MODEL.predict_proba(samples)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "f1_score": float(f1_score(labels, predictions)),
        "roc_auc": float(roc_auc_score(labels, probabilities)),
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_model(), indent=2))
