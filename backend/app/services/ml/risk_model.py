from __future__ import annotations

from typing import Any

WEIGHTS = {
    "de_ratio_norm": 0.22,
    "profitability_risk": 0.20,
    "gst_mismatch": 0.10,
    "bank_cashflow_risk": 0.10,
    "litigation_cases_norm": 0.14,
    "negative_news_score": 0.12,
    "sector_risk_score": 0.07,
    "revenue_decline_risk": 0.05,
}


def score_risk(feature_vector: dict[str, Any]) -> dict[str, Any]:
    weighted_contributions: dict[str, float] = {}
    score = 0.0

    for feature, weight in WEIGHTS.items():
        value = float(feature_vector.get(feature, 0.0) or 0.0)
        contribution = value * weight
        weighted_contributions[feature] = round(contribution, 4)
        score += contribution

    normalized_score = max(0.0, min(1.0, score))

    return {
        "risk_score": round(normalized_score, 4),
        "weighted_contributions": weighted_contributions,
    }
