from __future__ import annotations

import os
import re
from typing import Any


def dashboard_summary(state: dict[str, Any]) -> dict[str, Any]:
    deals = list(state.get("deals", []))
    companies_analyzed = len(deals)
    low_risk = sum(1 for deal in deals if deal.get("risk_category") == "Low Risk")
    medium_risk = sum(1 for deal in deals if deal.get("risk_category") == "Medium Risk")
    high_risk = sum(1 for deal in deals if deal.get("risk_category") == "High Risk")
    avg_risk_score = (
        round(sum(float(deal.get("risk_score") or 0) for deal in deals) / companies_analyzed, 4)
        if companies_analyzed
        else 0
    )
    return {
        "companies_analyzed": companies_analyzed,
        "low_risk": low_risk,
        "medium_risk": medium_risk,
        "high_risk": high_risk,
        "avg_risk_score": avg_risk_score,
    }


def dashboard_deals(state: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        list(state.get("deals", [])),
        key=lambda deal: str(deal.get("timestamp", "")),
        reverse=True,
    )


def portfolio_summary(state: dict[str, Any]) -> dict[str, Any]:
    deals = list(state.get("deals", []))
    total_exposure = sum(_parse_amount(deal.get("loan_limit", "0")) for deal in deals)
    return {
        "companies_analyzed": len(deals),
        "total_exposure": total_exposure,
        "low_risk": sum(1 for deal in deals if deal.get("risk_category") == "Low Risk"),
        "medium_risk": sum(1 for deal in deals if deal.get("risk_category") == "Medium Risk"),
        "high_risk": sum(1 for deal in deals if deal.get("risk_category") == "High Risk"),
    }


def portfolio_alerts(
    state: dict[str, Any],
    required_doc_types: set[str],
) -> list[str]:
    alerts: list[str] = []
    threshold = _high_risk_threshold()

    for deal in state.get("deals", []):
        company_name = deal.get("company_name", "Unknown Company")
        risk_score = deal.get("risk_score", 0)
        risk_category = deal.get("risk_category", "")
        loan_decision = deal.get("loan_decision", "")
        if risk_score >= threshold:
            alerts.append(f"{company_name}: High risk score ({risk_score:.2f}) - {risk_category}")
        if loan_decision == "Reject":
            alerts.append(f"{company_name}: Loan application rejected - {risk_category}")
        if loan_decision == "Review":
            alerts.append(f"{company_name}: Manual review required - {risk_category}")

    for entity_data in state.get("entities", {}).values():
        uploaded_files = entity_data.get("uploaded_files", [])
        if not uploaded_files:
            continue
        approved_types = {
            classification.get("detected_type") or classification.get("predicted_type")
            for classification in entity_data.get("classifications", [])
            if classification.get("approved")
        }
        missing_types = required_doc_types - {item for item in approved_types if item}
        if missing_types:
            company_name = entity_data.get("company_name", "Unknown Company")
            alerts.append(
                f"{company_name}: Missing required document types: {', '.join(sorted(missing_types))}"
            )
    return alerts


def portfolio_companies(state: dict[str, Any]) -> list[dict[str, Any]]:
    deal_map = _deal_map(state)
    companies = []
    for entity_id, entity_data in state.get("entities", {}).items():
        company_name = entity_data.get("company_name", "")
        if not company_name:
            continue
        deal_data = deal_map.get(company_name.lower(), {})
        companies.append(
            {
                "company_name": company_name,
                "entity_id": entity_id,
                "sector": entity_data.get("sector", "N/A"),
                "annual_turnover": entity_data.get("annual_turnover"),
                "loan_type": entity_data.get("loan_type"),
                "loan_amount": entity_data.get("loan_amount"),
                "exposure": _parse_amount(deal_data.get("loan_limit", "0")),
                "risk_score": deal_data.get("risk_score"),
                "risk_category": deal_data.get("risk_category"),
                "loan_limit": deal_data.get("loan_limit"),
                "interest_rate": deal_data.get("interest_rate"),
                "loan_decision": deal_data.get("loan_decision"),
                "created_at": entity_data.get("created_at"),
            }
        )
    return sorted(companies, key=lambda company: company["company_name"])


def portfolio_high_risk(state: dict[str, Any]) -> list[dict[str, Any]]:
    high_risk_companies = []
    deal_map = _deal_map(state)
    threshold = _high_risk_threshold()
    for entity_id, entity_data in state.get("entities", {}).items():
        company_name = entity_data.get("company_name", "")
        deal_data = deal_map.get(company_name.lower())
        if not company_name or not deal_data or deal_data.get("risk_score", 0) < threshold:
            continue
        high_risk_companies.append(
            {
                "company_name": company_name,
                "entity_id": entity_id,
                "risk_score": deal_data.get("risk_score"),
                "risk_category": deal_data.get("risk_category"),
                "loan_limit": deal_data.get("loan_limit"),
                "interest_rate": deal_data.get("interest_rate"),
                "loan_decision": deal_data.get("loan_decision"),
                "timestamp": deal_data.get("timestamp"),
                "sector": entity_data.get("sector", "N/A"),
            }
        )
    return sorted(high_risk_companies, key=lambda company: company["risk_score"], reverse=True)


def _deal_map(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(deal.get("company_name", "")).lower(): deal
        for deal in state.get("deals", [])
        if deal.get("company_name")
    }


def _parse_amount(value: Any) -> float:
    text = str(value or "0")
    return float(re.sub(r"[^\d.]", "", text)) if text else 0


def _high_risk_threshold() -> float:
    return float(os.getenv("HIGH_RISK_THRESHOLD", "0.6"))
