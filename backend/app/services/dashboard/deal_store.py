from __future__ import annotations

from typing import Any

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import Lock


@dataclass
class DealRecord:
    company_name: str
    risk_score: float
    risk_category: str
    loan_limit: str
    interest_rate: str
    decision_status: str
    financial_analysis: dict[str, Any]
    external_intelligence: dict[str, Any]
    risk_decision: dict[str, Any]
    timestamp: str


_DEALS: list[DealRecord] = []
_LOCK = Lock()


def add_deal(
    *,
    company_name: str,
    risk_score: float,
    risk_category: str,
    loan_limit: str,
    interest_rate: str,
    decision_status: str,
    financial_analysis: dict[str, Any] | None = None,
    external_intelligence: dict[str, Any] | None = None,
    risk_decision: dict[str, Any] | None = None,
) -> DealRecord:
    record = DealRecord(
        company_name=company_name.strip() or "Unknown Company",
        risk_score=round(float(risk_score), 2),
        risk_category=risk_category,
        loan_limit=loan_limit,
        interest_rate=interest_rate,
        decision_status=decision_status,
        financial_analysis=financial_analysis or {},
        external_intelligence=external_intelligence or {},
        risk_decision=risk_decision or {},
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    with _LOCK:
        _DEALS.append(record)

    return record


def list_deals() -> list[dict[str, str | float]]:
    with _LOCK:
        # Newest first keeps dashboard focused on latest decisions.
        return [asdict(record) for record in reversed(_DEALS)]
