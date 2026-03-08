from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.ml import build_credit_decision, build_feature_vector, get_top_risk_factors, score_risk

router = APIRouter(tags=["risk-score"])


class RiskScoreRequest(BaseModel):
    financial_analysis: dict[str, Any] = Field(default_factory=dict)
    external_intelligence: dict[str, Any] = Field(default_factory=dict)


@router.post("/risk-score")
async def run_risk_score(payload: RiskScoreRequest) -> dict[str, Any]:
    features = build_feature_vector(payload.financial_analysis, payload.external_intelligence)
    model_result = score_risk(features)

    risk_score = float(model_result.get("risk_score", 0.0) or 0.0)
    decision = build_credit_decision(risk_score=risk_score, revenue=float(features.get("revenue", 0.0) or 0.0))
    top_factors = get_top_risk_factors(model_result.get("weighted_contributions", {}))

    return {
        **decision,
        "top_risk_factors": top_factors,
        "feature_vector": {
            "de_ratio": features.get("debt_equity_ratio", 0.0),
            "ebitda_margin": features.get("ebitda_margin", 0.0),
            "revenue_growth": features.get("revenue_growth", 0.0),
            "gst_mismatch": features.get("gst_mismatch", 0.0),
            "bank_cashflow": features.get("bank_cashflow", 0.0),
            "litigation_cases": features.get("litigation_cases", 0.0),
            "negative_news_score": features.get("negative_news_score", 0.0),
            "sector_risk_score": features.get("sector_risk_score", 0.0),
        },
    }
