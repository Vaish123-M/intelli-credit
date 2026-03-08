from __future__ import annotations

from collections import Counter

from app.services.dashboard.deal_store import list_deals


def get_dashboard_summary() -> dict[str, int]:
    deals = list_deals()
    counts = Counter((deal.get("risk_category") or "").strip() for deal in deals)

    return {
        "companies_analyzed": len(deals),
        "low_risk": counts.get("Low Risk", 0),
        "medium_risk": counts.get("Medium Risk", 0),
        "high_risk": counts.get("High Risk", 0) + counts.get("Reject", 0),
    }
