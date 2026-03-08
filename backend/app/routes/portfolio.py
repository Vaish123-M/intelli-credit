from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.services.portfolio import get_high_risk_companies, get_portfolio_alerts, get_portfolio_summary, list_portfolio_records

router = APIRouter(prefix='/portfolio', tags=['portfolio'])


@router.get('/summary')
async def portfolio_summary() -> dict[str, int | float]:
    return get_portfolio_summary()


@router.get('/alerts')
async def portfolio_alerts() -> list[str]:
    return get_portfolio_alerts()


@router.get('/companies')
async def portfolio_companies() -> list[dict[str, Any]]:
    return list_portfolio_records()


@router.get('/high-risk')
async def portfolio_high_risk() -> list[dict[str, Any]]:
    return get_high_risk_companies()
