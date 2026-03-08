from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.analyzer import run_credit_analysis
from app.services.parser import parse_csv_file, parse_pdf_file

router = APIRouter(tags=["upload"])

LATEST_CONTEXT: dict[str, Any] = {"uploaded_files": [], "extracted_data": []}
LATEST_ANALYSIS: dict[str, Any] = {}


@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)) -> dict[str, Any]:
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded")

    extracted_data: list[dict[str, Any]] = []
    uploaded_files: list[dict[str, str]] = []

    for file in files:
        filename = file.filename or "unnamed_file"
        lower_name = filename.lower()
        content = await file.read()

        if not content:
            continue

        if lower_name.endswith(".csv"):
            parsed = parse_csv_file(content, filename, file.content_type)
        elif lower_name.endswith(".pdf"):
            parsed = parse_pdf_file(content, filename, file.content_type)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {filename}")

        extracted_data.append(parsed)
        uploaded_files.append({"filename": filename, "content_type": file.content_type or "unknown"})

    if not extracted_data:
        raise HTTPException(status_code=400, detail="No readable files were uploaded")

    analysis = run_credit_analysis(extracted_data)

    LATEST_CONTEXT["uploaded_files"] = uploaded_files
    LATEST_CONTEXT["extracted_data"] = extracted_data
    LATEST_ANALYSIS.clear()
    LATEST_ANALYSIS.update(analysis)

    return {
        "uploaded_files": uploaded_files,
        "extracted_data": extracted_data,
        "analysis": analysis,
    }


@router.post("/analyze")
async def analyze_latest_upload() -> dict[str, Any]:
    extracted_data = LATEST_CONTEXT.get("extracted_data", [])
    if not extracted_data:
        raise HTTPException(status_code=400, detail="No uploaded data found. Upload files first.")

    analysis = run_credit_analysis(extracted_data)
    LATEST_ANALYSIS.clear()
    LATEST_ANALYSIS.update(analysis)

    return {
        **analysis,
        "risk_flags": analysis.get("risk_flags", []),
        "extracted_data": extracted_data,
    }


@router.get("/results")
async def get_latest_results() -> dict[str, Any]:
    if not LATEST_CONTEXT.get("uploaded_files"):
        raise HTTPException(status_code=404, detail="No results found yet")

    return {
        "uploaded_files": LATEST_CONTEXT["uploaded_files"],
        "extracted_data": LATEST_CONTEXT["extracted_data"],
        "analysis": LATEST_ANALYSIS,
    }
