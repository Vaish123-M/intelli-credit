from __future__ import annotations

from typing import Any

from app.services.bank_analyzer import analyze_bank_statements
from app.services.gst_checker import analyze_gst_mismatch


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)


def analyze_financial_signals(extracted_files: list[dict[str, Any]]) -> dict[str, Any]:
    total_revenue = 0.0
    total_debt = 0.0
    total_equity = 0.0
    total_ebitda = 0.0

    revenue_series: list[float] = []

    for file_data in extracted_files:
        metrics = file_data.get("metrics", {})

        revenue = float(metrics.get("revenue", 0.0) or 0.0)
        debt = float(metrics.get("debt", 0.0) or 0.0)
        equity = float(metrics.get("equity", 0.0) or 0.0)
        ebitda = float(metrics.get("ebitda", 0.0) or 0.0)

        total_revenue += revenue
        total_debt += debt
        total_equity += equity
        total_ebitda += ebitda

        if revenue > 0:
            revenue_series.append(revenue)

    debt_to_equity = _safe_divide(total_debt, total_equity)

    revenue_growth = 0.0
    if len(revenue_series) >= 2:
        previous_revenue = revenue_series[-2]
        current_revenue = revenue_series[-1]
        revenue_growth = _safe_divide((current_revenue - previous_revenue), previous_revenue)

    ebitda_margin = _safe_divide(total_ebitda, total_revenue)

    risk_flags: list[str] = []
    if debt_to_equity > 2:
        risk_flags.append("High leverage")
    if ebitda_margin < 0.10:
        risk_flags.append("Low profitability")
    if revenue_growth < 0:
        risk_flags.append("Negative revenue growth")

    return {
        "revenue": round(total_revenue, 2),
        "debt_equity_ratio": round(debt_to_equity, 4),
        "revenue_growth": round(revenue_growth, 4),
        "ebitda_margin": round(ebitda_margin, 4),
        "risk_flags": risk_flags,
    }


def run_credit_analysis(extracted_files: list[dict[str, Any]]) -> dict[str, Any]:
    financial = analyze_financial_signals(extracted_files)
    gst = analyze_gst_mismatch(extracted_files)
    bank = analyze_bank_statements(extracted_files)

    risk_flags = list(financial.get("risk_flags", []))
    if gst.get("gst_mismatch"):
        risk_flags.append("GST mismatch above threshold")
    if bank.get("has_unusual_credit_spikes"):
        risk_flags.append("Unusual credit spikes detected")

    deduped_risk_flags: list[str] = []
    for flag in risk_flags:
        if flag not in deduped_risk_flags:
            deduped_risk_flags.append(flag)

    return {
        "revenue": financial.get("revenue", 0.0),
        "debt_equity_ratio": financial.get("debt_equity_ratio", 0.0),
        "ebitda_margin": financial.get("ebitda_margin", 0.0),
        "revenue_growth": financial.get("revenue_growth", 0.0),
        "gst_mismatch": gst.get("gst_mismatch", False),
        "gst_difference_percent": gst.get("difference_percent", 0.0),
        "gstr2a_total": gst.get("gstr2a_total", 0.0),
        "gstr3b_total": gst.get("gstr3b_total", 0.0),
        "bank_total_credits": bank.get("total_credits", 0.0),
        "bank_total_debits": bank.get("total_debits", 0.0),
        "bank_cashflow": bank.get("cashflow", 0.0),
        "bank_credit_spike_count": bank.get("unusual_spike_count", 0),
        "risk_flags": deduped_risk_flags,
    }


def run_basic_analysis(extracted_files: list[dict[str, Any]]) -> dict[str, Any]:
    return run_credit_analysis(extracted_files)
