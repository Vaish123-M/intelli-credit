from __future__ import annotations


def _format_currency_inr(value: float) -> str:
    if value >= 10_000_000:
        return f"INR {value / 10_000_000:.2f} Cr"
    if value >= 100_000:
        return f"INR {value / 100_000:.2f} L"
    return f"INR {value:.0f}"


def build_credit_decision(risk_score: float, revenue: float) -> dict[str, str | float]:
    if risk_score > 0.8:
        risk_category = "Reject"
        interest_rate = "N/A"
        loan_limit_value = 0.0
    elif risk_score > 0.6:
        risk_category = "High Risk"
        interest_rate = "13%"
        loan_limit_value = max(0.0, revenue * 0.08)
    elif risk_score > 0.3:
        risk_category = "Medium Risk"
        interest_rate = "11.5%"
        loan_limit_value = max(0.0, revenue * 0.08)
    else:
        risk_category = "Low Risk"
        interest_rate = "10.5%"
        loan_limit_value = max(0.0, revenue * 0.08)

    return {
        "risk_score": round(risk_score, 2),
        "risk_category": risk_category,
        "loan_limit": _format_currency_inr(loan_limit_value),
        "interest_rate": interest_rate,
    }
