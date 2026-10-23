from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field


router = APIRouter(tags=["operations"])


class CopilotRequest(BaseModel):
    company_data: dict[str, Any] = Field(default_factory=dict)
    question: str = ""


def _handler(request: Request, name: str) -> Callable[..., Any]:
    return request.app.state.operation_handlers[name]


@router.get("/audit/events")
def audit_events(request: Request, entity_id: str | None = None, limit: int = 100) -> dict[str, Any]:
    return _handler(request, "audit_events")(entity_id=entity_id, limit=limit)


@router.get("/dashboard/summary")
def dashboard_summary(request: Request) -> dict[str, Any]:
    return _handler(request, "dashboard_summary")()


@router.get("/dashboard/deals")
def dashboard_deals(request: Request) -> list[dict[str, Any]]:
    return _handler(request, "dashboard_deals")()


@router.post("/copilot/ask")
def copilot_ask(payload: CopilotRequest, request: Request) -> dict[str, str]:
    return _handler(request, "copilot_ask")(payload)


@router.get("/portfolio/summary")
def portfolio_summary(request: Request) -> dict[str, Any]:
    return _handler(request, "portfolio_summary")()


@router.get("/portfolio/alerts")
def portfolio_alerts(request: Request) -> list[str]:
    return _handler(request, "portfolio_alerts")()


@router.get("/portfolio/companies")
def portfolio_companies(request: Request) -> list[dict[str, Any]]:
    return _handler(request, "portfolio_companies")()


@router.get("/portfolio/high-risk")
def portfolio_high_risk(request: Request) -> list[dict[str, Any]]:
    return _handler(request, "portfolio_high_risk")()
