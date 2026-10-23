from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field


router = APIRouter(tags=["research", "risk"])


class ResearchRequest(BaseModel):
    company_name: str
    promoter_name: str | None = None
    entity_id: str | None = None


class RiskScoreRequest(BaseModel):
    company_name: str = "Unknown Company"
    financial_analysis: dict[str, Any] = Field(default_factory=dict)
    external_intelligence: dict[str, Any] = Field(default_factory=dict)


def _handler(request: Request, name: str) -> Callable[..., Any]:
    return request.app.state.research_handlers[name]


@router.post("/research")
def research(payload: ResearchRequest, request: Request) -> dict[str, Any]:
    return _handler(request, "research")(payload)


@router.post("/risk-score")
def risk_score(payload: RiskScoreRequest, request: Request) -> dict[str, Any]:
    return _handler(request, "risk_score")(payload)
