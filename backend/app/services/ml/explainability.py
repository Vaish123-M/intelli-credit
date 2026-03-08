from __future__ import annotations

from typing import Any

FEATURE_LABELS = {
    "de_ratio_norm": "High debt-to-equity ratio",
    "profitability_risk": "Low EBITDA margin",
    "gst_mismatch": "GST mismatch detected",
    "bank_cashflow_risk": "Weak bank cashflow health",
    "litigation_cases_norm": "Litigation cases detected",
    "negative_news_score": "Negative media sentiment",
    "sector_risk_score": "Elevated sector risk",
    "revenue_decline_risk": "Revenue decline trend",
}


def get_top_risk_factors(weighted_contributions: dict[str, float], top_n: int = 3) -> list[str]:
    ranked = sorted(weighted_contributions.items(), key=lambda item: item[1], reverse=True)
    top = [item for item in ranked if item[1] > 0.0][:top_n]

    if not top:
        return ["No major risk drivers detected"]

    factors: list[str] = []
    for key, _ in top:
        label = FEATURE_LABELS.get(key)
        if label and label not in factors:
            factors.append(label)

    return factors[:top_n]
