from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.cam import build_cam_sections, format_cam_markdown, generate_cam_pdf

router = APIRouter(tags=["cam"])

DOWNLOADS_DIR = Path(__file__).resolve().parents[2] / "downloads"


class CAMRequest(BaseModel):
    company_name: str = Field(..., min_length=2)
    financial_analysis: dict[str, Any] = Field(default_factory=dict)
    external_intelligence: dict[str, Any] = Field(default_factory=dict)
    risk_decision: dict[str, Any] = Field(default_factory=dict)


@router.post("/generate-cam")
async def generate_cam(payload: CAMRequest) -> dict[str, str]:
    sections = build_cam_sections(
        company_name=payload.company_name,
        financial_analysis=payload.financial_analysis,
        external_intelligence=payload.external_intelligence,
        risk_decision=payload.risk_decision,
    )

    markdown_report = format_cam_markdown(
        company_name=payload.company_name,
        sections=sections,
        risk_decision=payload.risk_decision,
    )

    file_name = generate_cam_pdf(
        company_name=payload.company_name,
        markdown_report=markdown_report,
        output_dir=DOWNLOADS_DIR,
    )

    return {"cam_report_url": f"/downloads/{file_name}"}
