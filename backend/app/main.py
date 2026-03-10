from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
import pdfplumber
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pypdf import PdfReader

APP_ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS_DIR = APP_ROOT / "downloads"
UPLOADS_DIR = APP_ROOT / "uploads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Intelli-Credit API", version="0.2.0")

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("intelli_credit.parser")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

state: dict[str, Any] = {
    "uploaded_files": [],
    "extracted_data": [],
    "analysis": None,
    "research": None,
    "decision": None,
    "deals": [],
    "entities": {},
    "current_entity_id": None,
}


class EntityOnboardRequest(BaseModel):
    company_name: str
    cin: str
    pan: str
    sector: str
    annual_turnover: float
    loan_type: str
    loan_amount: float
    loan_tenure: str
    interest_rate: float


class ResearchRequest(BaseModel):
    company_name: str
    promoter_name: str | None = None


class RiskScoreRequest(BaseModel):
    company_name: str = "Unknown Company"
    financial_analysis: dict[str, Any] = Field(default_factory=dict)
    external_intelligence: dict[str, Any] = Field(default_factory=dict)


class CamRequest(BaseModel):
    company_name: str
    financial_analysis: dict[str, Any] = Field(default_factory=dict)
    external_intelligence: dict[str, Any] = Field(default_factory=dict)
    risk_decision: dict[str, Any] = Field(default_factory=dict)


class CopilotRequest(BaseModel):
    company_data: dict[str, Any] = Field(default_factory=dict)
    question: str = ""


def _resolve_entity_id(entity_id: str | None = None) -> str | None:
    requested = (entity_id or "").strip()
    if requested:
        return requested

    current = state.get("current_entity_id")
    return str(current).strip() if current else None


def _get_entity_bucket(entity_id: str) -> dict[str, Any]:
    entities = state.setdefault("entities", {})
    entity_bucket = entities.get(entity_id)
    if not entity_bucket:
        raise HTTPException(status_code=404, detail="Invalid entity_id. Please onboard entity first.")
    return entity_bucket


def _extract_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages)

    return path.read_text(encoding="utf-8", errors="ignore")


def _normalize_column_name(column_name: Any) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", str(column_name or "").strip().lower())
    return cleaned.strip("_") or "col"


def _clean_numeric_value(raw: Any) -> int | None:
    if raw is None:
        return None
    # Keep only number-friendly characters and remove currency/symbol noise like "■".
    cleaned = re.sub(r"[^0-9,.-]", "", str(raw))
    if cleaned in {"", "-", ".", ","}:
        return None

    cleaned = cleaned.replace(",", "")
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def _is_metric_label(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in ["revenue", "sales", "turnover", "ebitda", "debt", "equity", "net worth", "borrowings"])


def _parse_financial_dataframe(df: pd.DataFrame, page_idx: int, table_idx: int) -> dict[str, int]:
    parsed: dict[str, int] = {}
    if df.empty or len(df.columns) < 2:
        return parsed

    df = df.fillna("")
    df.columns = [_normalize_column_name(col) for col in df.columns]
    logger.debug("Extracted table (page=%s, table=%s):\n%s", page_idx, table_idx, df.to_string(index=False))

    metric_col = None
    for col in df.columns:
        sample = " ".join(df[col].astype(str).head(12).tolist())
        if _is_metric_label(sample):
            metric_col = col
            break

    if metric_col is None:
        metric_col = df.columns[0]

    value_cols = [c for c in df.columns if c != metric_col]
    if not value_cols:
        return parsed

    year_candidates = []
    for col in value_cols:
        year_match = re.search(r"(19|20)\d{2}", col)
        if year_match:
            year_candidates.append((int(year_match.group(0)), col))

    if year_candidates:
        year_candidates.sort(key=lambda item: item[0])
        current_col = year_candidates[-1][1]
        previous_col = year_candidates[-2][1] if len(year_candidates) > 1 else None
    else:
        # Choose rightmost column with most numeric values.
        scored_cols = []
        for col in value_cols:
            numeric_hits = sum(1 for v in df[col].tolist() if _clean_numeric_value(v) is not None)
            scored_cols.append((numeric_hits, col))
        scored_cols.sort(key=lambda item: item[0])
        current_col = scored_cols[-1][1] if scored_cols else value_cols[-1]
        previous_col = value_cols[-2] if len(value_cols) > 1 else None

    for _, row in df.iterrows():
        label = str(row.get(metric_col, "")).strip().lower()
        current_val = _clean_numeric_value(row.get(current_col))
        previous_val = _clean_numeric_value(row.get(previous_col)) if previous_col else None

        if current_val is None or not _is_metric_label(label):
            continue

        if any(k in label for k in ["revenue", "sales", "turnover"]):
            parsed["revenue"] = current_val
            if previous_val is not None:
                parsed["revenue_previous"] = previous_val
        elif "ebitda" in label:
            parsed["ebitda"] = current_val
        elif "equity" in label or "net worth" in label or "shareholder" in label:
            parsed["equity"] = current_val
        elif "total debt" in label or "borrowings" in label or label == "debt" or label.endswith(" debt"):
            parsed["debt"] = current_val

    return parsed


def _extract_financials_from_text_table(text: str) -> dict[str, int]:
    parsed: dict[str, int] = {}
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    rows: list[list[str]] = []

    for line in lines:
        if "|" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 3:
                rows.append(parts)
        else:
            # Fallback for space-delimited rows
            parts = re.split(r"\s{2,}", line)
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) >= 3:
                rows.append(parts)

    if len(rows) < 2:
        return parsed

    header = rows[0]
    body = rows[1:]
    normalized_rows = []
    for r in body:
        if len(r) < len(header):
            r = r + [""] * (len(header) - len(r))
        normalized_rows.append(r[: len(header)])

    df = pd.DataFrame(normalized_rows, columns=header)
    parsed = _parse_financial_dataframe(df, page_idx=0, table_idx=0)
    if parsed:
        logger.debug("Parsed financial values from text-table fallback: %s", parsed)
    return parsed


def _extract_financials_from_csv(path: Path) -> dict[str, int]:
    parsed: dict[str, int] = {}
    try:
        df = pd.read_csv(path)
    except Exception:  # noqa: BLE001
        try:
            df = pd.read_csv(path, encoding="latin-1")
        except Exception:  # noqa: BLE001
            return parsed

    parsed = _parse_financial_dataframe(df, page_idx=0, table_idx=1)
    if parsed:
        logger.debug("Parsed financial values from CSV: %s", parsed)
    return parsed


def _extract_financials_from_pdf_tables(path: Path) -> dict[str, int]:
    parsed: dict[str, int] = {}

    with pdfplumber.open(str(path)) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            table_candidates = []
            strategies = [
                {},
                {"vertical_strategy": "text", "horizontal_strategy": "text"},
                {"snap_tolerance": 3, "join_tolerance": 3, "edge_min_length": 3},
            ]
            for settings in strategies:
                try:
                    table_candidates.extend(page.extract_tables(table_settings=settings) or [])
                except Exception:  # noqa: BLE001
                    continue

            for table_idx, table in enumerate(table_candidates, start=1):
                if not table or len(table) < 2:
                    continue

                raw_columns = table[0]
                rows = table[1:]
                df = pd.DataFrame(rows, columns=raw_columns)
                table_parsed = _parse_financial_dataframe(df, page_idx, table_idx)
                parsed.update(table_parsed)

            # If regular table extraction fails, try parsing text as table-like rows.
            if not parsed:
                text_fallback = _extract_financials_from_text_table(page.extract_text() or "")
                parsed.update(text_fallback)

    logger.debug("Parsed financial values from PDF tables: %s", parsed)
    return parsed


def _parse_number(raw: str) -> float:
    text = raw.lower().replace(",", "").strip()
    mult = 1.0
    if "crore" in text or "cr" in text:
        mult = 10_000_000.0
    elif "lakh" in text or "lac" in text:
        mult = 100_000.0
    elif "million" in text:
        mult = 1_000_000.0
    elif "billion" in text:
        mult = 1_000_000_000.0

    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return 0.0
    return float(match.group(0)) * mult


def _value_for_keywords(text: str, *keywords: str) -> float | None:
    pattern = r"(?:" + "|".join(re.escape(k) for k in keywords) + r")[^\d\n]{0,40}([\d,]+(?:\.\d+)?(?:\s*(?:cr|crore|lakh|lac|million|billion))?)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    return _parse_number(match.group(1))


def _extract_metrics(text: str) -> dict[str, float]:
    revenue = _value_for_keywords(text, "revenue", "sales", "turnover")
    debt = _value_for_keywords(text, "total debt", "borrowings", "debt")
    equity = _value_for_keywords(text, "net worth", "equity", "shareholder funds")
    ebitda = _value_for_keywords(text, "ebitda", "operating profit")

    bank_credits = _value_for_keywords(text, "total credits", "credits")
    bank_debits = _value_for_keywords(text, "total debits", "debits")
    gst_turnover = _value_for_keywords(text, "gst turnover", "gst sales")

    values = [_parse_number(v) for v in re.findall(r"[\d,]+(?:\.\d+)?(?:\s*(?:cr|crore|lakh|lac|million|billion))?", text, flags=re.IGNORECASE)]
    values = [v for v in values if v > 0]

    if revenue is None and values:
        revenue = max(values)

    # Do not inject synthetic values; preserve extraction truth.
    debt = debt if debt is not None else 0.0
    equity = equity if equity is not None else 0.0
    ebitda = ebitda if ebitda is not None else 0.0
    bank_credits = bank_credits if bank_credits is not None else 0.0
    bank_debits = bank_debits if bank_debits is not None else 0.0
    gst_turnover = gst_turnover if gst_turnover is not None else 0.0

    return {
        "revenue": float(revenue or 0.0),
        "debt": float(debt or 0.0),
        "equity": float(equity or 0.0),
        "ebitda": float(ebitda or 0.0),
        "bank_credits": float(bank_credits or 0.0),
        "bank_debits": float(bank_debits or 0.0),
        "gst_turnover": float(gst_turnover or 0.0),
        "revenue_previous": 0.0,
    }


def _merge_metrics(table_metrics: dict[str, int], text_metrics: dict[str, float]) -> dict[str, float]:
    merged = dict(text_metrics)
    for metric in ["revenue", "ebitda", "debt", "equity", "revenue_previous"]:
        if table_metrics.get(metric) is not None:
            merged[metric] = float(table_metrics[metric])
    return merged


def _build_analysis(extracted_data: list[dict[str, Any]]) -> dict[str, Any]:
    if not extracted_data:
        return {
            "revenue": None,
            "ebitda": None,
            "debt": None,
            "equity": None,
            "debt_equity_ratio": None,
            "ebitda_margin": None,
            "gst_mismatch": False,
            "gst_difference_percent": None,
            "bank_cashflow": None,
            "bank_total_credits": None,
            "bank_total_debits": None,
            "revenue_growth": None,
            "risk_flags": ["No parsable files"],
        }

    revenue = sum(item["metrics"]["revenue"] for item in extracted_data)
    revenue_previous = sum(item["metrics"].get("revenue_previous", 0.0) for item in extracted_data)
    debt = sum(item["metrics"]["debt"] for item in extracted_data)
    equity = sum(item["metrics"]["equity"] for item in extracted_data)
    ebitda = sum(item["metrics"]["ebitda"] for item in extracted_data)
    bank_credits = sum(item["metrics"]["bank_credits"] for item in extracted_data)
    bank_debits = sum(item["metrics"]["bank_debits"] for item in extracted_data)
    gst_turnover = sum(item["metrics"]["gst_turnover"] for item in extracted_data)

    debt_equity_ratio = (debt / equity) if equity > 0 else None
    ebitda_margin = (ebitda / revenue) if revenue > 0 else None
    gst_difference_percent = (abs(gst_turnover - revenue) / revenue * 100) if (revenue > 0 and gst_turnover > 0) else None
    gst_mismatch = (gst_difference_percent or 0) > 10
    bank_cashflow = bank_credits - bank_debits
    revenue_growth = ((revenue - revenue_previous) / revenue_previous) if revenue_previous > 0 else None

    flags: list[str] = []
    if debt_equity_ratio is not None and debt_equity_ratio > 2.0:
        flags.append("High leverage")
    if ebitda_margin is not None and ebitda_margin < 0.10:
        flags.append("Low operating margin")
    if revenue_growth is not None and revenue_growth < 0:
        flags.append("Declining business")
    if gst_mismatch:
        flags.append("GST turnover mismatch")
    if bank_cashflow < 0:
        flags.append("Negative bank cashflow")

    if revenue <= 0:
        flags.append("Revenue not extracted")

    final_metrics = {
        "revenue": round(revenue, 2) if revenue > 0 else None,
        "ebitda": round(ebitda, 2) if ebitda > 0 else None,
        "debt": round(debt, 2) if debt > 0 else None,
        "equity": round(equity, 2) if equity > 0 else None,
        "debt_equity_ratio": round(debt_equity_ratio, 4) if debt_equity_ratio is not None else None,
        "ebitda_margin": round(ebitda_margin, 4) if ebitda_margin is not None else None,
        "gst_mismatch": gst_mismatch,
        "gst_difference_percent": round(gst_difference_percent, 2) if gst_difference_percent is not None else None,
        "bank_cashflow": round(bank_cashflow, 2) if (bank_credits > 0 or bank_debits > 0) else None,
        "bank_total_credits": round(bank_credits, 2) if bank_credits > 0 else None,
        "bank_total_debits": round(bank_debits, 2) if bank_debits > 0 else None,
        "revenue_growth": round(revenue_growth, 4) if revenue_growth is not None else None,
        "risk_flags": flags,
    }
    logger.debug("Final calculated metrics: %s", final_metrics)
    return final_metrics


def _sector_from_name(name: str) -> tuple[str, str]:
    n = name.lower()
    if any(k in n for k in ["infra", "construction", "steel"]):
        return "Infrastructure", "High"
    if any(k in n for k in ["pharma", "health"]):
        return "Pharma", "Low"
    if any(k in n for k in ["textile", "garment"]):
        return "Textiles", "Medium"
    return "General", "Medium"


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "intelli-credit-api"}


@app.post("/entity-onboard")
def entity_onboard(payload: EntityOnboardRequest) -> dict[str, Any]:
    entity_id = f"ent_{uuid4().hex[:12]}"
    entity_record = {
        "entity_id": entity_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "company_name": payload.company_name,
        "cin": payload.cin,
        "pan": payload.pan,
        "sector": payload.sector,
        "annual_turnover": payload.annual_turnover,
        "loan_type": payload.loan_type,
        "loan_amount": payload.loan_amount,
        "loan_tenure": payload.loan_tenure,
        "interest_rate": payload.interest_rate,
        "uploaded_files": [],
        "extracted_data": [],
        "analysis": None,
    }

    entities = state.setdefault("entities", {})
    entities[entity_id] = entity_record
    state["current_entity_id"] = entity_id

    return {
        "entity_id": entity_id,
        "entity": entity_record,
        "message": "Entity onboarded successfully.",
    }


@app.post("/upload")
async def upload(entity_id: str = Form(...), files: list[UploadFile] = File(...)) -> dict[str, Any]:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    resolved_entity_id = _resolve_entity_id(entity_id)
    if not resolved_entity_id:
        raise HTTPException(status_code=400, detail="entity_id is required. Please complete onboarding first.")
    entity_bucket = _get_entity_bucket(resolved_entity_id)

    uploaded_files: list[dict[str, Any]] = []
    extracted_data: list[dict[str, Any]] = []

    for upload_file in files:
        safe_name = upload_file.filename or f"upload_{datetime.utcnow().timestamp():.0f}.bin"
        target = UPLOADS_DIR / safe_name
        content = await upload_file.read()
        target.write_bytes(content)

        parsed_text = _extract_text(target)
        text_metrics = _extract_metrics(parsed_text)
        table_metrics: dict[str, int] = {}
        if target.suffix.lower() == ".pdf":
            try:
                table_metrics = _extract_financials_from_pdf_tables(target)
            except Exception as table_error:  # noqa: BLE001
                logger.exception("Table parsing failed for %s: %s", target.name, table_error)
        elif target.suffix.lower() == ".csv":
            table_metrics = _extract_financials_from_csv(target)
        else:
            table_metrics = _extract_financials_from_text_table(parsed_text)

        metrics = _merge_metrics(table_metrics, text_metrics)
        logger.debug("Metrics after merge (%s): %s", target.name, metrics)

        uploaded_files.append(
            {
                "entity_id": resolved_entity_id,
                "filename": safe_name,
                "saved_path": str(target),
                "size_bytes": len(content),
            }
        )
        extracted_data.append(
            {
                "entity_id": resolved_entity_id,
                "filename": safe_name,
                "char_count": len(parsed_text),
                "detected_sections": ["balance_sheet", "pnl", "cashflow"],
                "metrics": metrics,
            }
        )

    analysis = _build_analysis(extracted_data)
    state["uploaded_files"] = uploaded_files
    state["extracted_data"] = extracted_data
    state["analysis"] = analysis
    state["current_entity_id"] = resolved_entity_id

    entity_bucket["uploaded_files"] = uploaded_files
    entity_bucket["extracted_data"] = extracted_data
    entity_bucket["analysis"] = analysis

    return {
        "entity_id": resolved_entity_id,
        "uploaded_files": uploaded_files,
        "extracted_data": extracted_data,
        "analysis": analysis,
    }


@app.post("/analyze")
def analyze(entity_id: str | None = None) -> dict[str, Any]:
    resolved_entity_id = _resolve_entity_id(entity_id)
    if resolved_entity_id:
        entity_bucket = _get_entity_bucket(resolved_entity_id)
        extracted_data = entity_bucket.get("extracted_data", [])
    else:
        extracted_data = state.get("extracted_data", [])

    analysis = _build_analysis(extracted_data)
    state["analysis"] = analysis
    if resolved_entity_id:
        entity_bucket["analysis"] = analysis
        state["current_entity_id"] = resolved_entity_id

    return {"entity_id": resolved_entity_id, "analysis": analysis, "extracted_data": extracted_data}


@app.get("/results")
def results(entity_id: str | None = None) -> dict[str, Any]:
    resolved_entity_id = _resolve_entity_id(entity_id)
    if resolved_entity_id:
        entity_bucket = _get_entity_bucket(resolved_entity_id)
        return {
            "entity_id": resolved_entity_id,
            "uploaded_files": entity_bucket.get("uploaded_files", []),
            "extracted_data": entity_bucket.get("extracted_data", []),
            "analysis": entity_bucket.get("analysis"),
        }

    return {
        "entity_id": None,
        "uploaded_files": state.get("uploaded_files", []),
        "extracted_data": state.get("extracted_data", []),
        "analysis": state.get("analysis"),
    }


@app.post("/research")
def research(payload: ResearchRequest) -> dict[str, Any]:
    sector, sector_risk = _sector_from_name(payload.company_name)
    litigation_cases = 0 if sector_risk == "Low" else (1 if sector_risk == "Medium" else 3)
    high_risk_cases = 0 if sector_risk != "High" else 1
    negative_news_score = 0.22 if sector_risk == "Low" else (0.37 if sector_risk == "Medium" else 0.61)

    promoter_sentiment = "Positive" if negative_news_score < 0.3 else ("Neutral" if negative_news_score < 0.5 else "Negative")
    intelligence = {
        "negative_news_score": round(negative_news_score, 2),
        "news_articles_found": 12,
        "litigation_cases": litigation_cases,
        "high_risk_cases": high_risk_cases,
        "sector_risk": sector_risk,
        "sector": sector,
        "promoter_sentiment": promoter_sentiment,
        "promoter_sentiment_confidence": 0.73,
        "errors": [],
    }

    state["research"] = intelligence
    return {"financial_analysis": state.get("analysis") or {}, "external_intelligence": intelligence}


@app.post("/risk-score")
def risk_score(payload: RiskScoreRequest) -> dict[str, Any]:
    analysis = payload.financial_analysis or {}
    intelligence = payload.external_intelligence or {}

    leverage = float(analysis.get("debt_equity_ratio", 1.2) or 1.2)
    margin = float(analysis.get("ebitda_margin", 0.12) or 0.12)
    gst_mismatch = bool(analysis.get("gst_mismatch", False))
    news_risk = float(intelligence.get("negative_news_score", 0.35) or 0.35)
    litigation = int(intelligence.get("high_risk_cases", 0) or 0)

    risk = 0.45 + (0.18 if leverage > 2 else 0.08) + (0.14 if margin < 0.1 else 0.03) + news_risk * 0.22 + (0.09 if gst_mismatch else 0) + min(litigation * 0.06, 0.12)
    risk = min(max(risk, 0.05), 0.99)

    if risk >= 0.72:
        risk_category = "High Risk"
        loan_limit = "INR 25,00,000"
        interest_rate = "18.50%"
    elif risk >= 0.5:
        risk_category = "Medium Risk"
        loan_limit = "INR 75,00,000"
        interest_rate = "14.25%"
    else:
        risk_category = "Low Risk"
        loan_limit = "INR 1,50,00,000"
        interest_rate = "11.50%"

    factors = list(analysis.get("risk_flags", []))
    if news_risk > 0.5:
        factors.append("Adverse media sentiment")
    if litigation > 0:
        factors.append("Open high-risk litigation")
    if not factors:
        factors = ["No major adverse signals"]

    decision = {
        "company_name": payload.company_name,
        "risk_score": round(risk, 4),
        "risk_category": risk_category,
        "loan_limit": loan_limit,
        "interest_rate": interest_rate,
        "top_risk_factors": factors,
        "decision_status": "Approved" if risk_category == "Low Risk" else ("Review Required" if risk_category == "Medium Risk" else "Rejected"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    state["decision"] = decision

    # Keep one latest analysis per company for dashboard aggregation.
    existing_deals: list[dict[str, Any]] = list(state.get("deals", []))
    existing_deals = [deal for deal in existing_deals if str(deal.get("company_name", "")).lower() != payload.company_name.lower()]
    existing_deals.append(decision)
    state["deals"] = existing_deals

    return decision


@app.post("/generate-cam")
def generate_cam(payload: CamRequest) -> dict[str, str]:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r"[^a-zA-Z0-9_]+", "_", payload.company_name.lower()).strip("_") or "company"
    report_name = f"cam_report_{safe_name}_{timestamp}.txt"
    report_path = DOWNLOADS_DIR / report_name

    report_path.write_text(
        "\n".join(
            [
                "INTELLI-CREDIT CAM REPORT",
                f"Company: {payload.company_name}",
                f"Generated At (UTC): {datetime.utcnow().isoformat()}Z",
                "",
                "Financial Analysis:",
                str(payload.financial_analysis),
                "",
                "External Intelligence:",
                str(payload.external_intelligence),
                "",
                "Risk Decision:",
                str(payload.risk_decision),
            ]
        ),
        encoding="utf-8",
    )

    return {"cam_report_url": f"/downloads/{report_name}"}


@app.get("/downloads/{filename}")
def get_download(filename: str) -> FileResponse:
    file_path = DOWNLOADS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path=file_path, filename=file_path.name, media_type="text/plain")


@app.get("/dashboard/summary")
def dashboard_summary() -> dict[str, Any]:
    deals = list(state.get("deals", []))
    companies_analyzed = len(deals)
    low_risk = sum(1 for deal in deals if deal.get("risk_category") == "Low Risk")
    medium_risk = sum(1 for deal in deals if deal.get("risk_category") == "Medium Risk")
    high_risk = sum(1 for deal in deals if deal.get("risk_category") == "High Risk")
    avg_risk_score = round(sum(float(deal.get("risk_score") or 0) for deal in deals) / companies_analyzed, 4) if companies_analyzed else 0

    return {
        "companies_analyzed": companies_analyzed,
        "low_risk": low_risk,
        "medium_risk": medium_risk,
        "high_risk": high_risk,
        "avg_risk_score": avg_risk_score,
    }


@app.get("/dashboard/deals")
def dashboard_deals() -> list[dict[str, Any]]:
    deals = list(state.get("deals", []))
    return sorted(deals, key=lambda deal: str(deal.get("timestamp", "")), reverse=True)


@app.post("/copilot/ask")
def copilot_ask(payload: CopilotRequest) -> dict[str, str]:
    prompt = payload.question.strip() or "No question provided"
    return {"answer": f"Copilot insight: '{prompt}' mapped to uploaded credit signals."}


@app.get("/portfolio/summary")
def portfolio_summary() -> dict[str, Any]:
    return {
        "companies_analyzed": 42,
        "total_exposure": 512_400_000,
        "low_risk": 20,
        "medium_risk": 14,
        "high_risk": 8,
    }


@app.get("/portfolio/alerts")
def portfolio_alerts() -> list[str]:
    return [
        "Zenith Foods: DSCR dropped below threshold",
        "Argo Logistics: delayed statutory filing",
    ]


@app.get("/portfolio/companies")
def portfolio_companies() -> list[dict[str, Any]]:
    return [
        {"company_name": "Apex Metals", "exposure": 74_500_000, "risk_score": 0.61},
        {"company_name": "Nova Textiles", "exposure": 58_100_000, "risk_score": 0.29},
        {"company_name": "Zenith Foods", "exposure": 42_800_000, "risk_score": 0.81},
    ]


@app.get("/portfolio/high-risk")
def portfolio_high_risk() -> list[dict[str, Any]]:
    return [
        {
            "company_name": "Zenith Foods",
            "risk_score": 0.81,
            "loan_limit": 25_000_00,
            "interest_rate": "18.50%",
            "timestamp": "2026-03-10T08:35:00Z",
        },
        {
            "company_name": "Triton Infra",
            "risk_score": 0.76,
            "loan_limit": 35_000_00,
            "interest_rate": "17.25%",
            "timestamp": "2026-03-10T08:42:00Z",
        },
    ]
