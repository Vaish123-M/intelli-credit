from __future__ import annotations

from typing import Any


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _append_unique(items: list[str], text: str) -> None:
    if text and text not in items:
        items.append(text)


def generate_swot_analysis(
    financial_metrics: dict[str, Any],
    risk_analysis: dict[str, Any],
    secondary_research_signals: dict[str, Any],
) -> dict[str, list[str]]:
    metrics = financial_metrics or {}
    risk = risk_analysis or {}
    research = secondary_research_signals or {}
    research_features = research.get("research_features") or {}

    leverage = _as_float(metrics.get("debt_equity_ratio"), 1.5)
    margin = _as_float(metrics.get("ebitda_margin"), 0.1)
    revenue_growth = metrics.get("revenue_growth")
    bank_cashflow = metrics.get("bank_cashflow")
    gst_mismatch = bool(metrics.get("gst_mismatch", False))

    risk_score = _as_float(risk.get("risk_score"), 0.5)
    decision_status = str(risk.get("loan_decision") or risk.get("decision_status") or "Review")

    sector_outlook = str(research.get("sector_outlook") or "Moderate growth expected")
    market_sentiment = str(research.get("market_sentiment") or "Neutral")
    litigation_signal = _as_float(research_features.get("litigation_signal"), 0.0)
    negative_news_signal = _as_float(research_features.get("negative_news_signal"), _as_float(research.get("negative_news_score"), 0.35))
    sector_growth_signal = _as_float(research_features.get("sector_growth_signal"), 0.5)

    strengths: list[str] = []
    weaknesses: list[str] = []
    opportunities: list[str] = []
    threats: list[str] = []

    if margin >= 0.15:
        _append_unique(strengths, "High EBITDA margin")
    elif margin < 0.1:
        _append_unique(weaknesses, "Low EBITDA margin")

    if isinstance(revenue_growth, (int, float)):
        if revenue_growth > 0.05:
            _append_unique(strengths, "Positive revenue growth")
        elif revenue_growth < 0:
            _append_unique(weaknesses, "Declining revenue trend")

    if leverage <= 1.2:
        _append_unique(strengths, "Low debt-to-equity ratio")
    elif leverage <= 2.0:
        _append_unique(weaknesses, "Moderate leverage")
    else:
        _append_unique(weaknesses, "High leverage")

    if isinstance(bank_cashflow, (int, float)):
        if bank_cashflow > 0:
            _append_unique(strengths, "Positive operating cashflow")
        elif bank_cashflow < 0:
            _append_unique(weaknesses, "Negative bank cashflow")

    if gst_mismatch:
        _append_unique(weaknesses, "GST mismatch flagged in submitted data")

    if sector_growth_signal >= 0.6 or "strong" in sector_outlook.lower() or "moderate" in sector_outlook.lower():
        _append_unique(opportunities, "Growing sector demand")

    if market_sentiment == "Positive":
        _append_unique(opportunities, "Positive market sentiment can improve pricing power")

    if decision_status == "Approve":
        _append_unique(opportunities, "Eligible for faster credit turnaround")
    elif decision_status == "Review":
        _append_unique(opportunities, "Potential to improve rating through tighter controls")

    if negative_news_signal >= 0.55:
        _append_unique(threats, "Adverse media coverage risk")

    if litigation_signal >= 0.45:
        _append_unique(threats, "Ongoing or emerging litigation exposure")

    if market_sentiment == "Negative":
        _append_unique(threats, "Weak market sentiment may pressure demand")

    if risk_score > 0.7:
        _append_unique(threats, "Elevated default risk profile")

    if sector_growth_signal < 0.45:
        _append_unique(threats, "Sector slowdown risk")

    if not strengths:
        strengths = ["Stable baseline financial indicators"]
    if not weaknesses:
        weaknesses = ["No material internal weaknesses detected"]
    if not opportunities:
        opportunities = ["Incremental growth opportunities from portfolio diversification"]
    if not threats:
        threats = ["No immediate external threats identified"]

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "opportunities": opportunities,
        "threats": threats,
    }
