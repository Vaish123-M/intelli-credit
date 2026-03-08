from __future__ import annotations

from typing import Any

from app.services.copilot.prompt_builder import build_credit_prompt


def _as_percent(value: Any) -> str:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return "N/A"
    if score <= 1:
        score *= 100
    return f"{round(score)}%"


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _extract_top_financial_risks(financial_analysis: dict[str, Any]) -> list[str]:
    risks: list[str] = []

    de_ratio = _float(financial_analysis.get("debt_equity_ratio"))
    if de_ratio > 1.5:
        risks.append("Debt-to-equity is elevated, increasing leverage risk.")

    ebitda_margin = _float(financial_analysis.get("ebitda_margin"))
    if 0 < ebitda_margin < 0.15:
        risks.append("EBITDA margin is thin, reducing repayment buffer.")

    growth = _float(financial_analysis.get("revenue_growth_rate", financial_analysis.get("revenue_growth")))
    if growth < 0.02:
        risks.append("Revenue growth is low, signaling slower business momentum.")

    gst_mismatch = _float(
        financial_analysis.get(
            "gst_sales_vs_financial_sales_mismatch_pct",
            financial_analysis.get("gst_mismatch_pct", 0),
        )
    )
    if gst_mismatch > 10:
        risks.append("High GST mismatch indicates possible reporting inconsistencies.")

    bank_cashflow = _float(financial_analysis.get("bank_cashflow", financial_analysis.get("average_monthly_inflow", 0)))
    if bank_cashflow <= 0:
        risks.append("Bank cashflow appears weak, reducing liquidity comfort.")

    return risks


def answer_credit_question(
    *,
    company_name: str,
    financial_analysis: dict[str, Any],
    external_intelligence: dict[str, Any],
    risk_decision: dict[str, Any],
    question: str,
) -> str:
    # Prompt is generated for compatibility with future LLM integrations.
    _ = build_credit_prompt(
        company_name=company_name,
        financial_analysis=financial_analysis,
        external_intelligence=external_intelligence,
        risk_decision=risk_decision,
        question=question,
    )

    q = question.lower().strip()
    risk_category = str(risk_decision.get("risk_category", "Unknown")).strip() or "Unknown"
    risk_score = _as_percent(risk_decision.get("risk_score"))
    decision_status = str(risk_decision.get("decision_status", "Review Required"))
    loan_limit = str(risk_decision.get("loan_limit", "N/A"))
    interest_rate = str(risk_decision.get("interest_rate", "N/A"))

    top_factors = risk_decision.get("top_risk_factors") or []
    top_factors = [str(item) for item in top_factors if str(item).strip()]

    financial_risks = _extract_top_financial_risks(financial_analysis)

    litigation = external_intelligence.get("litigation", {}) if isinstance(external_intelligence, dict) else {}
    sector = external_intelligence.get("sector_risk", {}) if isinstance(external_intelligence, dict) else {}
    sentiment = external_intelligence.get("market_sentiment", {}) if isinstance(external_intelligence, dict) else {}

    sector_level = str(sector.get("level", sector.get("risk_level", "Unknown")))
    sentiment_label = str(sentiment.get("label", "Unknown"))
    litigation_level = str(litigation.get("risk_level", "Unknown"))

    if "why" in q and "risk" in q:
        drivers = top_factors[:3] if top_factors else financial_risks[:3]
        if not drivers:
            drivers = ["Current risk appears to be driven by a combination of financial and sector signals."]
        joined_drivers = " ".join([f"- {item}" for item in drivers])
        return (
            f"{company_name} is classified as {risk_category} with a risk score of {risk_score}. "
            f"Key drivers: {joined_drivers} "
            f"External context: sector risk is {sector_level}, litigation risk is {litigation_level}, "
            f"and market sentiment is {sentiment_label}."
        )

    if "biggest" in q or "financial" in q:
        points = financial_risks[:3]
        if not points:
            points = ["No major financial red flags were detected from the current extracted metrics."]
        joined_points = " ".join([f"- {item}" for item in points])
        return f"Top financial risk view for {company_name}: {joined_points}"

    if "approve" in q or "loan" in q or "should we" in q:
        return (
            f"Current recommendation for {company_name}: {decision_status}. "
            f"Model output is {risk_category} ({risk_score}), with loan limit {loan_limit} and interest rate {interest_rate}. "
            "Use this as decision support alongside policy, collateral checks, and committee judgment."
        )

    return (
        f"Summary for {company_name}: risk category {risk_category} (score {risk_score}), decision status {decision_status}, "
        f"loan limit {loan_limit}, interest rate {interest_rate}. "
        f"External signals show sector risk {sector_level}, litigation risk {litigation_level}, and sentiment {sentiment_label}."
    )
