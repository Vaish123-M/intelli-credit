from __future__ import annotations

from typing import Any


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)


def analyze_gst_mismatch(extracted_files: list[dict[str, Any]], threshold: float = 0.10) -> dict[str, Any]:
    gstr2a_total = 0.0
    gstr3b_total = 0.0

    for file_data in extracted_files:
        category = file_data.get("category")
        metrics = file_data.get("metrics", {})
        gst_total = float(metrics.get("gst_total", 0.0) or 0.0)

        if category == "gst_gstr2a":
            gstr2a_total += gst_total
        elif category == "gst_gstr3b":
            gstr3b_total += gst_total

    difference_ratio = _safe_divide(abs(gstr2a_total - gstr3b_total), gstr3b_total if gstr3b_total else 1.0)
    difference_percent = difference_ratio * 100

    return {
        "gst_mismatch": difference_ratio > threshold,
        "difference_percent": round(difference_percent, 2),
        "gstr2a_total": round(gstr2a_total, 2),
        "gstr3b_total": round(gstr3b_total, 2),
    }
