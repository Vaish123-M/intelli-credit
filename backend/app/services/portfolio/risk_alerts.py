from __future__ import annotations

from app.services.portfolio.portfolio_metrics import get_portfolio_summary

HIGH_RISK_RATIO_THRESHOLD = 0.25
TOTAL_EXPOSURE_THRESHOLD = 500_000_000


def get_portfolio_alerts() -> list[str]:
    summary = get_portfolio_summary()

    companies = int(summary.get('companies_analyzed', 0) or 0)
    high_risk = int(summary.get('high_risk', 0) or 0)
    exposure = float(summary.get('total_exposure', 0.0) or 0.0)

    alerts: list[str] = []

    if companies > 0 and (high_risk / companies) > HIGH_RISK_RATIO_THRESHOLD:
        alerts.append('High-risk exposure exceeds 25%')

    if exposure > TOTAL_EXPOSURE_THRESHOLD:
        alerts.append('Portfolio concentration risk detected')

    return alerts
