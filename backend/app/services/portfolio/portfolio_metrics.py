from __future__ import annotations

from collections import Counter

from app.services.portfolio.portfolio_store import list_portfolio_records


def _normalize_category(value: str | None) -> str:
    category = (value or '').strip().casefold()
    if category in {'low risk', 'low'}:
        return 'Low Risk'
    if category in {'medium risk', 'medium'}:
        return 'Medium Risk'
    if category in {'high risk', 'high', 'reject'}:
        return 'High Risk'
    return 'Unknown'


def get_portfolio_summary() -> dict[str, int | float]:
    records = list_portfolio_records()
    counts = Counter(_normalize_category(str(record.get('risk_category') or '')) for record in records)
    total_exposure = sum(float(record.get('loan_limit', 0.0) or 0.0) for record in records)

    return {
        'companies_analyzed': len(records),
        'total_exposure': round(total_exposure, 2),
        'low_risk': counts.get('Low Risk', 0),
        'medium_risk': counts.get('Medium Risk', 0),
        'high_risk': counts.get('High Risk', 0),
    }


def get_high_risk_companies() -> list[dict[str, str | float]]:
    records = list_portfolio_records()
    return [
        record
        for record in records
        if _normalize_category(str(record.get('risk_category', ''))) == 'High Risk'
        or float(record.get('risk_score', 0.0) or 0.0) >= 0.6
    ]
