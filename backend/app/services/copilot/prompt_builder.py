from __future__ import annotations

from typing import Any


def build_credit_prompt(
    *,
    company_name: str,
    financial_analysis: dict[str, Any],
    external_intelligence: dict[str, Any],
    risk_decision: dict[str, Any],
    question: str,
) -> str:
    return (
        "You are a credit risk analyst.\n\n"
        f"Company: {company_name}\n\n"
        "Financial Metrics:\n"
        f"{financial_analysis}\n\n"
        "External Intelligence:\n"
        f"{external_intelligence}\n\n"
        "Risk Decision:\n"
        f"{risk_decision}\n\n"
        "User Question:\n"
        f"{question}\n\n"
        "Provide a clear and concise explanation."
    )
