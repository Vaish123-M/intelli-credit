from __future__ import annotations

from typing import Any


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_credit_recommendation(
    financial_metrics: dict[str, Any],
    risk_score: float,
    secondary_research_signals: dict[str, Any],
) -> dict[str, Any]:
    metrics = financial_metrics or {}
    research = secondary_research_signals or {}
    research_features = research.get("research_features") or {}

    leverage = _as_float(metrics.get("debt_equity_ratio"), 1.5)
    margin = _as_float(metrics.get("ebitda_margin"), 0.1)
    revenue_growth = metrics.get("revenue_growth")
    gst_mismatch = bool(metrics.get("gst_mismatch", False))

    news_signal = _as_float(research_features.get("negative_news_signal"), _as_float(research.get("negative_news_score"), 0.35))
    litigation_signal = _as_float(research_features.get("litigation_signal"), 0.0)
    sector_growth_signal = _as_float(research_features.get("sector_growth_signal"), 0.5)
    market_sentiment = str(research.get("market_sentiment") or "Neutral")

    if risk_score < 0.4:
        decision = "Approve"
        interest_rate = "11.50%"
        loan_limit = "INR 1,50,00,000"
    elif risk_score <= 0.7:
        decision = "Review"
        interest_rate = "14.25%"
        loan_limit = "INR 75,00,000"
    else:
        decision = "Reject"
        interest_rate = "18.50%"
        loan_limit = "INR 25,00,000"

    reasoning: list[str] = []

    if leverage < 1.2:
        reasoning.append("Low debt-to-equity ratio")
    elif leverage > 2.0:
        reasoning.append("High debt-to-equity ratio")

    if margin >= 0.15:
        reasoning.append("Strong EBITDA margin")
    elif margin < 0.1:
        reasoning.append("Weak EBITDA margin")

    if isinstance(revenue_growth, (int, float)):
        if revenue_growth > 0.05:
            reasoning.append("Positive revenue growth")
        elif revenue_growth < 0:
            reasoning.append("Negative revenue growth")

    if gst_mismatch:
        reasoning.append("GST mismatch observed in financial signals")

    if news_signal >= 0.6:
        reasoning.append("Recent negative news flow detected")

    if litigation_signal >= 0.6:
        reasoning.append("Elevated litigation risk from secondary research")

    if sector_growth_signal >= 0.6:
        reasoning.append("Sector growth trend supports business outlook")
    elif sector_growth_signal < 0.45:
        reasoning.append("Sector growth trend is weak")

    if market_sentiment == "Positive":
        reasoning.append("Market sentiment is positive")
    elif market_sentiment == "Negative":
        reasoning.append("Market sentiment is negative")

    if not reasoning:
        reasoning = ["Decision derived from composite financial, risk, and external intelligence signals"]

    return {
        "decision": decision,
        "risk_score": round(float(risk_score), 4),
        "reasoning": reasoning,
        "recommended_loan_limit": loan_limit,
        "recommended_interest_rate": interest_rate,
    }
