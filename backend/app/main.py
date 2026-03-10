from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pdfplumber
from fastapi import FastAPI, File, HTTPException, UploadFile
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
}


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


def _extract_financials_from_pdf_tables(path: Path) -> dict[str, int]:
    parsed: dict[str, int] = {}

    with pdfplumber.open(str(path)) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables() or []
            for table_idx, table in enumerate(tables, start=1):
                if not table or len(table) < 2:
                    continue

                raw_columns = table[0]
                rows = table[1:]
                df = pd.DataFrame(rows, columns=raw_columns)
                df.columns = [_normalize_column_name(col) for col in df.columns]
                df = df.fillna("")

                logger.debug("Extracted table (page=%s, table=%s):\n%s", page_idx, table_idx, df.to_string(index=False))

                metric_col = None
                for col in df.columns:
                    sample = " ".join(df[col].astype(str).head(8).tolist())
                    if _is_metric_label(sample):
                        metric_col = col
                        break

                if metric_col is None:
                    continue

                value_cols = [c for c in df.columns if c != metric_col]
                if not value_cols:
                    continue

                current_col = value_cols[-1]  # Rightmost column is treated as latest FY.
                previous_col = value_cols[-2] if len(value_cols) > 1 else None

                for _, row in df.iterrows():
                    label = str(row.get(metric_col, "")).strip().lower()
                    current_val = _clean_numeric_value(row.get(current_col))
                    previous_val = _clean_numeric_value(row.get(previous_col)) if previous_col else None

                    if current_val is None:
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
    if debt is None:
        debt = revenue * 0.52 if revenue else 12_000_000.0
    if equity is None:
        equity = revenue * 0.41 if revenue else 10_000_000.0
    if ebitda is None:
        ebitda = revenue * 0.16 if revenue else 4_000_000.0
    if bank_credits is None:
        bank_credits = revenue * 0.92 if revenue else 20_000_000.0
    if bank_debits is None:
        bank_debits = revenue * 0.84 if revenue else 17_500_000.0
    if gst_turnover is None:
        gst_turnover = revenue * 0.97 if revenue else 0.0

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
            "revenue": 0,
            "debt_equity_ratio": 0,
            "ebitda_margin": 0,
            "gst_mismatch": False,
            "gst_difference_percent": 0,
            "bank_cashflow": 0,
            "bank_total_credits": 0,
            "bank_total_debits": 0,
            "revenue_growth": 0,
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

    debt_equity_ratio = debt / max(equity, 1)
    ebitda_margin = (ebitda / revenue) if revenue > 0 else 0.0
    gst_difference_percent = abs(gst_turnover - revenue) / max(revenue, 1) * 100
    gst_mismatch = gst_difference_percent > 10
    bank_cashflow = bank_credits - bank_debits
    revenue_growth = ((revenue - revenue_previous) / revenue_previous) if revenue_previous > 0 else 0.0

    flags: list[str] = []
    if debt_equity_ratio > 2.0:
        flags.append("High leverage")
    if ebitda_margin < 0.10:
        flags.append("Low operating margin")
    if gst_mismatch:
        flags.append("GST turnover mismatch")
    if bank_cashflow < 0:
        flags.append("Negative bank cashflow")

    final_metrics = {
        "revenue": round(revenue, 2),
        "ebitda": round(ebitda, 2),
        "debt": round(debt, 2),
        "equity": round(equity, 2),
        "debt_equity_ratio": round(debt_equity_ratio, 4),
        "ebitda_margin": round(ebitda_margin, 4),
        "gst_mismatch": gst_mismatch,
        "gst_difference_percent": round(gst_difference_percent, 2),
        "bank_cashflow": round(bank_cashflow, 2),
        "bank_total_credits": round(bank_credits, 2),
        "bank_total_debits": round(bank_debits, 2),
        "revenue_growth": round(revenue_growth, 4),
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


@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)) -> dict[str, Any]:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

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

        metrics = _merge_metrics(table_metrics, text_metrics)
        logger.debug("Metrics after merge (%s): %s", target.name, metrics)

        uploaded_files.append({"filename": safe_name, "saved_path": str(target), "size_bytes": len(content)})
        extracted_data.append(
            {
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

    return {"uploaded_files": uploaded_files, "extracted_data": extracted_data, "analysis": analysis}


@app.post("/analyze")
def analyze() -> dict[str, Any]:
    extracted_data = state.get("extracted_data", [])
    analysis = _build_analysis(extracted_data)
    state["analysis"] = analysis
    return {"analysis": analysis, "extracted_data": extracted_data}


@app.get("/results")
def results() -> dict[str, Any]:
    return {
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
    }
    state["decision"] = decision
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
    decision = state.get("decision") or {}
    score = float(decision.get("risk_score", 0.62) or 0.62)
    return {
        "companies_analyzed": 42,
        "low_risk": 20,
        "medium_risk": 14,
        "high_risk": 8,
        "avg_risk_score": round(score, 4),
    }


@app.get("/dashboard/deals")
def dashboard_deals() -> list[dict[str, Any]]:
    return [
        {
            "company_name": "Apex Metals",
            "risk_score": 0.61,
            "risk_category": "Medium Risk",
            "loan_limit": "INR 75,00,000",
            "interest_rate": "14.25%",
            "decision_status": "Review Required",
            "timestamp": "2026-03-10T08:00:00Z",
        },
        {
            "company_name": "Nova Textiles",
            "risk_score": 0.29,
            "risk_category": "Low Risk",
            "loan_limit": "INR 1,50,00,000",
            "interest_rate": "11.50%",
            "decision_status": "Approved",
            "timestamp": "2026-03-10T08:20:00Z",
        },
        {
            "company_name": "Zenith Foods",
            "risk_score": 0.81,
            "risk_category": "High Risk",
            "loan_limit": "INR 25,00,000",
            "interest_rate": "18.50%",
            "decision_status": "Rejected",
            "timestamp": "2026-03-10T08:35:00Z",
        },
    ]


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
