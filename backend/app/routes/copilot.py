from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.copilot import answer_credit_question

router = APIRouter(prefix="/copilot", tags=["copilot"])


class CopilotAskRequest(BaseModel):
    company_data: dict[str, Any] = Field(default_factory=dict)
    question: str = Field(..., min_length=3)


@router.post("/ask")
async def ask_copilot(payload: CopilotAskRequest) -> dict[str, str]:
    company_data = payload.company_data or {}

    company_name = str(company_data.get("company_name", "Unknown Company"))
    financial_analysis = company_data.get("financial_analysis") or {}
    external_intelligence = company_data.get("external_intelligence") or {}
    risk_decision = company_data.get("risk_decision") or {}

    answer = answer_credit_question(
        company_name=company_name,
        financial_analysis=financial_analysis,
        external_intelligence=external_intelligence,
        risk_decision=risk_decision,
        question=payload.question,
    )

    return {"answer": answer}
