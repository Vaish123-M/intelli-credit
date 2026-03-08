from __future__ import annotations

import io
import re
from typing import Any

import fitz
import pandas as pd

FINANCIAL_KEYWORDS = ["revenue", "debt", "ebitda", "assets", "liabilities", "equity"]


def detect_document_category(filename: str, content_type: str | None = None) -> str:
    lower_name = filename.lower()

    if "gstr-2a" in lower_name or "gstr2a" in lower_name:
        return "gst_gstr2a"
    if "gstr-3b" in lower_name or "gstr3b" in lower_name:
        return "gst_gstr3b"
    if "bank" in lower_name or "statement" in lower_name:
        return "bank_statement"
    if "annual" in lower_name or "report" in lower_name:
        return "annual_report"
    if "financial" in lower_name or "balance" in lower_name or "p&l" in lower_name:
        return "financial_statement"

    if filename.lower().endswith(".csv"):
        return "csv_document"
    if filename.lower().endswith(".pdf"):
        if content_type and "pdf" in content_type.lower():
            return "financial_statement"
        return "pdf_document"
    return "unknown"


def parse_csv_file(file_bytes: bytes, filename: str, content_type: str | None = None) -> dict[str, Any]:
    category = detect_document_category(filename, content_type)

    dataframe = pd.read_csv(io.BytesIO(file_bytes))
    dataframe.columns = [str(column).strip() for column in dataframe.columns]

    row_count = int(len(dataframe.index))
    columns = dataframe.columns.tolist()
    lower_map = {column.lower(): column for column in columns}

    revenue_columns = [
        column
        for column in columns
        if any(token in column.lower() for token in ["revenue", "sales", "turnover", "income"])
    ]

    numeric_series: dict[str, pd.Series] = {}
    for column in columns:
        numeric_candidate = pd.to_numeric(dataframe[column], errors="coerce")
        if numeric_candidate.notna().any():
            numeric_series[column] = numeric_candidate.fillna(0)

    def sum_first_matching(possible_tokens: list[str]) -> float:
        matching_columns = [
            original for lowered, original in lower_map.items() if any(token in lowered for token in possible_tokens)
        ]
        total = 0.0
        for column in matching_columns:
            if column in numeric_series:
                total += float(numeric_series[column].sum())
        return total

    revenue_value = sum_first_matching(["revenue", "sales", "turnover", "income"])
    debt_value = sum_first_matching(["debt", "borrow", "loan"])
    equity_value = sum_first_matching(["equity", "networth", "net_worth", "shareholder"])
    ebitda_value = sum_first_matching(["ebitda", "operating profit"])

    gst_total = 0.0
    if category in {"gst_gstr2a", "gst_gstr3b"}:
        gst_total = sum_first_matching(["gst", "tax", "taxable", "igst", "cgst", "sgst"])

    total_credits = 0.0
    total_debits = 0.0
    cashflow = 0.0
    abnormal_spikes: list[float] = []
    if category == "bank_statement":
        credit_columns = [
            col
            for col in columns
            if any(token in col.lower() for token in ["credit", "deposit", "cr", "inflow"])
        ]
        debit_columns = [
            col
            for col in columns
            if any(token in col.lower() for token in ["debit", "withdraw", "dr", "outflow"])
        ]

        credit_series = None
        debit_series = None
        if credit_columns:
            credit_series = numeric_series.get(credit_columns[0])
        if debit_columns:
            debit_series = numeric_series.get(debit_columns[0])
        else:
            amount_column = next((col for col in columns if "amount" in col.lower()), None)
            if amount_column and amount_column in numeric_series:
                amount_series = numeric_series[amount_column]
                credit_series = amount_series
                debit_series = amount_series

        if credit_series is not None:
            total_credits = float(credit_series[credit_series > 0].sum())
            positive_values = credit_series[credit_series > 0]
            if not positive_values.empty:
                threshold = float(positive_values.mean() + (2 * positive_values.std(ddof=0)))
                abnormal_spikes = [float(value) for value in positive_values[positive_values > threshold].tolist()]

        if debit_series is not None:
            total_debits = float(abs(debit_series[debit_series < 0].sum()))
            if total_debits == 0.0:
                total_debits = float(debit_series[debit_series > 0].sum())

        cashflow = total_credits - total_debits

    return {
        "filename": filename,
        "kind": "csv",
        "category": category,
        "rows": row_count,
        "columns": columns,
        "revenue_columns": revenue_columns,
        "metrics": {
            "revenue": revenue_value,
            "debt": debt_value,
            "equity": equity_value,
            "ebitda": ebitda_value,
            "gst_total": gst_total,
            "total_credits": total_credits,
            "total_debits": total_debits,
            "cashflow": cashflow,
            "abnormal_spikes": abnormal_spikes,
        },
    }


def parse_pdf_file(file_bytes: bytes, filename: str, content_type: str | None = None) -> dict[str, Any]:
    category = detect_document_category(filename, content_type)

    with fitz.open(stream=file_bytes, filetype="pdf") as pdf_document:
        pages = [page.get_text("text") for page in pdf_document]

    text = "\n".join(pages)
    text_lower = text.lower()

    keyword_counts = {keyword: text_lower.count(keyword) for keyword in FINANCIAL_KEYWORDS}

    extracted_numbers: dict[str, list[float]] = {}
    for keyword in FINANCIAL_KEYWORDS:
        pattern = re.compile(rf"{keyword}[^0-9]{{0,30}}([\d,]+(?:\.\d+)?)", re.IGNORECASE)
        values = []
        for match in pattern.findall(text):
            sanitized = match.replace(",", "")
            try:
                values.append(float(sanitized))
            except ValueError:
                continue
        extracted_numbers[keyword] = values

    return {
        "filename": filename,
        "kind": "pdf",
        "category": category,
        "pages": len(pages),
        "text_preview": text[:1000],
        "keyword_counts": keyword_counts,
        "metrics": {
            "revenue": sum(extracted_numbers.get("revenue", [])),
            "debt": sum(extracted_numbers.get("debt", [])),
            "ebitda": sum(extracted_numbers.get("ebitda", [])),
            "assets": sum(extracted_numbers.get("assets", [])),
            "liabilities": sum(extracted_numbers.get("liabilities", [])),
            "equity": sum(extracted_numbers.get("equity", [])),
        },
    }
