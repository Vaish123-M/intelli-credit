from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


router = APIRouter(tags=["reports"])


class CamRequest(BaseModel):
    company_name: str
    entity_id: str | None = None
    financial_analysis: dict[str, Any] = Field(default_factory=dict)
    external_intelligence: dict[str, Any] = Field(default_factory=dict)
    risk_decision: dict[str, Any] = Field(default_factory=dict)


class FinalReportRequest(BaseModel):
    company_name: str
    entity_id: str | None = None
    financial_analysis: dict[str, Any] = Field(default_factory=dict)
    external_intelligence: dict[str, Any] = Field(default_factory=dict)
    risk_decision: dict[str, Any] = Field(default_factory=dict)


def _handler(request: Request, name: str) -> Callable[..., Any]:
    return request.app.state.report_handlers[name]


@router.post("/generate-cam")
def generate_cam(request: Request, payload: CamRequest) -> dict[str, str]:
    return _handler(request, "generate_cam")(payload)


@router.post("/generate-final-report")
def generate_final_report(request: Request, payload: FinalReportRequest) -> dict[str, str]:
    return _handler(request, "generate_final_report")(payload)


@router.get("/downloads/{filename}")
def get_download(filename: str, request: Request) -> FileResponse:
    return _handler(request, "get_download")(filename)
