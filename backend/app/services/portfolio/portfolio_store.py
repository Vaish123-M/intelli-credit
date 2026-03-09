from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import Lock


@dataclass
class PortfolioRecord:
    company_name: str
    risk_score: float
    risk_category: str
    loan_limit: float
    interest_rate: str
    timestamp: str


_RECORDS: list[PortfolioRecord] = []
_LOCK = Lock()


def _company_key(name: str) -> str:
    return (name or '').strip().casefold()


def _parse_loan_limit_to_inr(value: str | float | int | None) -> float:
    if value is None:
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(',', '')
    if not text:
        return 0.0

    if text.upper() == 'N/A':
        return 0.0

    # Supports values like "INR 33.60 L" and "INR 4.00 Cr".
    match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(CR|L)?', text, re.IGNORECASE)
    if not match:
        return 0.0

    amount = float(match.group(1))
    unit = (match.group(2) or '').upper()

    if unit == 'CR':
        return amount * 10_000_000
    if unit == 'L':
        return amount * 100_000
    return amount


def add_portfolio_record(
    *,
    company_name: str,
    risk_score: float,
    risk_category: str,
    loan_limit: str | float,
    interest_rate: str,
) -> PortfolioRecord:
    normalized_company_name = company_name.strip() or 'Unknown Company'
    record = PortfolioRecord(
        company_name=normalized_company_name,
        risk_score=round(float(risk_score), 2),
        risk_category=risk_category,
        loan_limit=round(_parse_loan_limit_to_inr(loan_limit), 2),
        interest_rate=interest_rate,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    with _LOCK:
        # Keep one latest portfolio profile per company to avoid double counting re-runs.
        company_key = _company_key(normalized_company_name)
        for index, existing_record in enumerate(_RECORDS):
            if _company_key(existing_record.company_name) == company_key:
                _RECORDS[index] = record
                break
        else:
            _RECORDS.append(record)

    return record


def list_portfolio_records() -> list[dict[str, str | float]]:
    with _LOCK:
        return [asdict(record) for record in reversed(_RECORDS)]
