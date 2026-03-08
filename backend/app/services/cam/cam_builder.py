from __future__ import annotations

from typing import Any


def _as_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def build_cam_sections(
    company_name: str,
    financial_analysis: dict[str, Any],
    external_intelligence: dict[str, Any],
    risk_decision: dict[str, Any],
) -> dict[str, str]:
    promoter_sentiment = external_intelligence.get("promoter_sentiment", "Neutral")
    litigation_cases = int(external_intelligence.get("litigation_cases", 0) or 0)
    negative_news_score = float(external_intelligence.get("negative_news_score", 0.0) or 0.0)

    ebitda_margin = float(financial_analysis.get("ebitda_margin", 0.0) or 0.0)
    revenue_growth = float(financial_analysis.get("revenue_growth", 0.0) or 0.0)
    debt_equity_ratio = float(financial_analysis.get("debt_equity_ratio", 0.0) or 0.0)
    revenue = float(financial_analysis.get("revenue", 0.0) or 0.0)
    bank_cashflow = float(financial_analysis.get("bank_cashflow", 0.0) or 0.0)

    risk_category = risk_decision.get("risk_category", "N/A")
    risk_score = float(risk_decision.get("risk_score", 0.0) or 0.0)
    loan_limit = risk_decision.get("loan_limit", "N/A")
    interest_rate = risk_decision.get("interest_rate", "N/A")

    character = (
        f"External intelligence for {company_name} indicates promoter sentiment is {promoter_sentiment}. "
        f"A total of {litigation_cases} litigation-related signals were identified, "
        f"with a negative news intensity score of {_as_percent(negative_news_score)}."
    )

    capacity = (
        f"Operating capacity remains supported by EBITDA margin of {_as_percent(ebitda_margin)} and "
        f"revenue growth of {_as_percent(revenue_growth)}. Debt-to-equity ratio stands at {debt_equity_ratio:.2f}, "
        "which is evaluated in conjunction with profitability and growth trend."
    )

    capital = (
        f"Capital structure review shows annualized revenue around INR {revenue:,.0f} with net bank cashflow of "
        f"INR {bank_cashflow:,.0f}. Current leverage and liquidity profile suggest a {risk_category} borrower profile."
    )

    collateral = (
        "Detailed collateral inventory is not fully digitized in this prototype. "
        "Collateral assessment is currently treated as a manual diligence checkpoint using asset schedules and security cover documents."
    )

    conditions = (
        f"Based on AI risk score ({risk_score:.2f}) and the derived risk category ({risk_category}), "
        f"the model recommends a provisional loan limit of {loan_limit} at an indicative interest rate of {interest_rate}."
    )

    return {
        "character": character,
        "capacity": capacity,
        "capital": capital,
        "collateral": collateral,
        "conditions": conditions,
    }
