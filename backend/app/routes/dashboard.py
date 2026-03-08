from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.services.dashboard import get_dashboard_summary, list_deals

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def dashboard_summary() -> dict[str, int]:
    return get_dashboard_summary()


@router.get("/deals")
async def dashboard_deals() -> list[dict[str, Any]]:
    return list_deals()
