from __future__ import annotations

from typing import Any


def _clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _sector_risk_score(sector_risk: str) -> float:
    mapping = {
        "low": 0.2,
        "medium": 0.5,
        "high": 0.85,
    }
    return mapping.get((sector_risk or "").lower(), 0.5)


def build_feature_vector(financial_analysis: dict[str, Any], external_intelligence: dict[str, Any]) -> dict[str, Any]:
    revenue = _to_float(financial_analysis.get("revenue"), 0.0)
    debt_equity_ratio = _to_float(financial_analysis.get("debt_equity_ratio"), 0.0)
    ebitda_margin = _to_float(financial_analysis.get("ebitda_margin"), 0.0)
    revenue_growth = _to_float(financial_analysis.get("revenue_growth"), 0.0)
    gst_mismatch = 1.0 if bool(financial_analysis.get("gst_mismatch")) else 0.0
    bank_cashflow = _to_float(financial_analysis.get("bank_cashflow"), 0.0)

    litigation_cases = _to_float(external_intelligence.get("litigation_cases"), 0.0)
    negative_news_score = _clamp(_to_float(external_intelligence.get("negative_news_score"), 0.0))
    sector_risk_score = _sector_risk_score(str(external_intelligence.get("sector_risk", "Medium")))

    de_ratio_norm = _clamp(debt_equity_ratio / 3.0)
    profitability_risk = _clamp(1.0 - ebitda_margin)
    litigation_cases_norm = _clamp(litigation_cases / 3.0)
    revenue_decline_risk = _clamp(max(0.0, -revenue_growth))

    bank_cashflow_risk = 0.0
    if bank_cashflow < 0:
        denominator = revenue if revenue > 0 else abs(bank_cashflow)
        bank_cashflow_risk = _clamp(abs(bank_cashflow) / (denominator if denominator > 0 else 1.0))

    return {
        "revenue": revenue,
        "debt_equity_ratio": debt_equity_ratio,
        "ebitda_margin": ebitda_margin,
        "revenue_growth": revenue_growth,
        "gst_mismatch": gst_mismatch,
        "bank_cashflow": bank_cashflow,
        "litigation_cases": litigation_cases,
        "negative_news_score": negative_news_score,
        "sector_risk_score": sector_risk_score,
        "de_ratio_norm": de_ratio_norm,
        "profitability_risk": profitability_risk,
        "litigation_cases_norm": litigation_cases_norm,
        "bank_cashflow_risk": bank_cashflow_risk,
        "revenue_decline_risk": revenue_decline_risk,
    }
