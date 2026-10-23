from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split


MODEL_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = MODEL_DIR / "credit_risk_model.joblib"
BENCHMARK_PATH = MODEL_DIR / "credit_risk_model_benchmark.json"
FEATURE_SCHEMA_PATH = MODEL_DIR / "credit_risk_feature_schema.json"
MODEL_VERSION = "logreg_v1"


@dataclass(frozen=True)
class RiskModelArtifacts:
    model_version: str
    feature_names: list[str]
    benchmark: dict[str, Any]
    threshold: float


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _build_feature_vector(
    financial_metrics: dict[str, Any],
    secondary_research_signals: dict[str, Any],
) -> tuple[list[float], list[str]]:
    metrics = financial_metrics or {}
    research = secondary_research_signals or {}
    research_features = research.get("research_features") or {}

    features = [
        _as_float(metrics.get("debt_equity_ratio"), 1.5),
        _as_float(metrics.get("ebitda_margin"), 0.1),
        _as_float(metrics.get("revenue_growth"), 0.0),
        1.0 if bool(metrics.get("gst_mismatch", False)) else 0.0,
        _as_float(research_features.get("negative_news_signal"), _as_float(research.get("negative_news_score"), 0.35)),
        _as_float(research_features.get("litigation_signal"), 0.0),
        _as_float(research_features.get("sector_growth_signal"), 0.5),
        _as_float(research_features.get("market_sentiment_signal"), 0.5),
    ]
    feature_names = [
        "debt_equity_ratio",
        "ebitda_margin",
        "revenue_growth",
        "gst_mismatch",
        "negative_news_signal",
        "litigation_signal",
        "sector_growth_signal",
        "market_sentiment_signal",
    ]
    return features, feature_names


def _training_samples() -> tuple[np.ndarray, np.ndarray]:
    samples = np.array(
        [
            [0.8, 0.24, 0.13, 0.0, 0.10, 0.00, 0.78, 0.20],
            [1.0, 0.18, 0.09, 0.0, 0.14, 0.02, 0.70, 0.28],
            [1.1, 0.16, 0.06, 0.0, 0.18, 0.05, 0.66, 0.35],
            [1.4, 0.13, 0.02, 0.0, 0.24, 0.07, 0.57, 0.45],
            [1.7, 0.11, 0.00, 0.0, 0.31, 0.10, 0.50, 0.55],
            [2.1, 0.09, -0.04, 1.0, 0.42, 0.18, 0.41, 0.72],
            [2.4, 0.07, -0.07, 1.0, 0.56, 0.26, 0.35, 0.80],
            [2.9, 0.05, -0.12, 1.0, 0.71, 0.40, 0.28, 0.88],
            [3.2, 0.04, -0.16, 1.0, 0.82, 0.55, 0.22, 0.92],
            [2.0, 0.10, -0.03, 1.0, 0.48, 0.14, 0.39, 0.69],
            [1.2, 0.19, 0.07, 0.0, 0.19, 0.01, 0.63, 0.31],
            [2.7, 0.06, -0.10, 1.0, 0.67, 0.36, 0.30, 0.85],
            [0.9, 0.23, 0.11, 0.0, 0.09, 0.00, 0.74, 0.22],
            [1.5, 0.14, 0.01, 0.0, 0.27, 0.06, 0.55, 0.48],
            [2.5, 0.08, -0.05, 1.0, 0.53, 0.22, 0.34, 0.77],
            [1.8, 0.12, 0.04, 0.0, 0.25, 0.08, 0.58, 0.50],
            [0.7, 0.26, 0.15, 0.0, 0.08, 0.00, 0.82, 0.18],
            [3.0, 0.03, -0.14, 1.0, 0.76, 0.48, 0.24, 0.91],
            [1.3, 0.17, 0.05, 0.0, 0.23, 0.03, 0.61, 0.34],
        ],
        dtype=float,
    )
    labels = np.array([0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0], dtype=int)
    return samples, labels


def train_model() -> RiskModelArtifacts:
    samples, labels = _training_samples()
    feature_names = [
        "debt_equity_ratio",
        "ebitda_margin",
        "revenue_growth",
        "gst_mismatch",
        "negative_news_signal",
        "litigation_signal",
        "sector_growth_signal",
        "market_sentiment_signal",
    ]

    x_train, x_test, y_train, y_test = train_test_split(
        samples,
        labels,
        test_size=0.33,
        random_state=42,
        stratify=labels,
    )

    model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    model.fit(x_train, y_train)

    probabilities = model.predict_proba(x_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)

    benchmark: dict[str, Any] = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "f1_score": float(f1_score(y_test, predictions)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "dataset_type": "synthetic_demo",
        "dataset_size": int(len(samples)),
        "test_size": 0.33,
        "random_state": 42,
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": model,
        "feature_names": feature_names,
        "threshold": 0.5,
        "model_version": MODEL_VERSION,
    }
    joblib.dump(payload, MODEL_PATH)
    BENCHMARK_PATH.write_text(json.dumps(benchmark, indent=2), encoding="utf-8")
    FEATURE_SCHEMA_PATH.write_text(
        json.dumps(
            {
                "model_version": MODEL_VERSION,
                "feature_names": feature_names,
                "thresholds": {
                    "approve_max_probability": 0.35,
                    "review_max_probability": 0.65,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return RiskModelArtifacts(MODEL_VERSION, feature_names, benchmark, 0.5)


def _load_or_train_model() -> tuple[LogisticRegression, list[str], float, RiskModelArtifacts]:
    if MODEL_PATH.exists():
        payload = joblib.load(MODEL_PATH)
        benchmark: dict[str, float] = {}
        if BENCHMARK_PATH.exists():
            try:
                benchmark = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                benchmark = {}
        artifacts = RiskModelArtifacts(
            model_version=str(payload.get("model_version") or MODEL_VERSION),
            feature_names=list(payload.get("feature_names") or []),
            benchmark=benchmark,
            threshold=float(payload.get("threshold") or 0.5),
        )
        return payload["model"], artifacts.feature_names, artifacts.threshold, artifacts

    raise RuntimeError(
        f"Risk model artifact is missing at {MODEL_PATH}. Run "
        "`python -m app.services.ml.train_model` before starting the API."
    )


MODEL, MODEL_FEATURE_NAMES, MODEL_THRESHOLD, MODEL_ARTIFACTS = _load_or_train_model()


def _feature_contributions(features: list[float], feature_names: list[str]) -> list[dict[str, Any]]:
    coefficients = getattr(MODEL, "coef_", [[0.0] * len(features)])[0]
    contributions = [
        {
            "feature": name,
            "value": round(value, 4),
            "contribution": round(float(coefficient) * value, 4),
            "direction": "increases_risk" if coefficient > 0 else "reduces_risk",
        }
        for name, value, coefficient in zip(feature_names, features, coefficients, strict=True)
    ]
    return sorted(contributions, key=lambda item: abs(item["contribution"]), reverse=True)


def _decision_from_probability(probability: float) -> str:
    if probability < 0.35:
        return "Approve"
    if probability <= 0.65:
        return "Review"
    return "Reject"


def _loan_terms_from_probability(probability: float) -> tuple[str, str, str]:
    if probability < 0.35:
        return "Low Risk", "INR 1,50,00,000", "11.50%"
    if probability <= 0.65:
        return "Medium Risk", "INR 75,00,000", "14.25%"
    return "High Risk", "INR 25,00,000", "18.50%"


def build_credit_recommendation(
    financial_metrics: dict[str, Any],
    risk_score: float | None,
    secondary_research_signals: dict[str, Any],
) -> dict[str, Any]:
    features, feature_names = _build_feature_vector(financial_metrics, secondary_research_signals)
    model_probability = float(MODEL.predict_proba([features])[0][1])
    external_score = _as_float(risk_score, model_probability)
    blended_risk_score = round((model_probability * 0.7) + (external_score * 0.3), 4)

    risk_category, loan_limit, interest_rate = _loan_terms_from_probability(model_probability)
    decision = _decision_from_probability(model_probability)

    reasoning: list[str] = []
    if features[0] < 1.2:
        reasoning.append("Low debt-to-equity ratio")
    elif features[0] > 2.0:
        reasoning.append("High debt-to-equity ratio")

    if features[1] >= 0.15:
        reasoning.append("Strong EBITDA margin")
    elif features[1] < 0.1:
        reasoning.append("Weak EBITDA margin")

    if features[2] > 0.05:
        reasoning.append("Positive revenue growth")
    elif features[2] < 0:
        reasoning.append("Negative revenue growth")

    if features[3] >= 1.0:
        reasoning.append("GST mismatch observed in financial signals")

    if features[4] >= 0.6:
        reasoning.append("Recent negative news flow detected")

    if features[5] >= 0.6:
        reasoning.append("Elevated litigation risk from secondary research")

    if features[6] >= 0.6:
        reasoning.append("Sector growth trend supports business outlook")
    elif features[6] < 0.45:
        reasoning.append("Sector growth trend is weak")

    if features[7] < 0.4:
        reasoning.append("Market sentiment is positive")
    elif features[7] > 0.7:
        reasoning.append("Market sentiment is negative")

    if not reasoning:
        reasoning = ["Decision derived from the trained credit risk model"]

    return {
        "decision": decision,
        "risk_score": blended_risk_score,
        "model_probability": round(model_probability, 4),
        "model_version": MODEL_ARTIFACTS.model_version,
        "benchmark": MODEL_ARTIFACTS.benchmark,
        "feature_names": feature_names,
        "feature_contributions": _feature_contributions(features, feature_names),
        "reasoning": reasoning,
        "recommended_loan_limit": loan_limit,
        "recommended_interest_rate": interest_rate,
        "risk_category": risk_category,
        "training_threshold": MODEL_THRESHOLD,
    }
