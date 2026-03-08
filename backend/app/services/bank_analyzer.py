from __future__ import annotations

from typing import Any


def analyze_bank_statements(extracted_files: list[dict[str, Any]]) -> dict[str, Any]:
    total_credits = 0.0
    total_debits = 0.0
    spike_count = 0

    for file_data in extracted_files:
        if file_data.get("category") != "bank_statement":
            continue

        metrics = file_data.get("metrics", {})
        total_credits += float(metrics.get("total_credits", 0.0) or 0.0)
        total_debits += float(metrics.get("total_debits", 0.0) or 0.0)

        spikes = metrics.get("abnormal_spikes", []) or []
        spike_count += len(spikes)

    cashflow = total_credits - total_debits

    return {
        "total_credits": round(total_credits, 2),
        "total_debits": round(total_debits, 2),
        "cashflow": round(cashflow, 2),
        "has_unusual_credit_spikes": spike_count > 0,
        "unusual_spike_count": spike_count,
    }
