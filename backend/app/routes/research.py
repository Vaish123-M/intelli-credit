from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.routes.upload import LATEST_ANALYSIS, LATEST_CONTEXT
from app.services.analyzer import run_credit_analysis
from app.services.research import (
    analyze_promoter_sentiment,
    analyze_sector_risk,
    check_litigation,
    fetch_news_intelligence,
)

router = APIRouter(tags=["research"])


class ResearchRequest(BaseModel):
    company_name: str = Field(..., min_length=2)
    promoter_name: str | None = None


@router.post("/research")
async def run_research(payload: ResearchRequest) -> dict[str, Any]:
    extracted_data = LATEST_CONTEXT.get("extracted_data", [])
    financial_analysis = dict(LATEST_ANALYSIS)

    if not financial_analysis and extracted_data:
        financial_analysis = run_credit_analysis(extracted_data)

    news = fetch_news_intelligence(payload.company_name, payload.promoter_name)
    litigation = check_litigation(payload.company_name)
    sector = analyze_sector_risk(payload.company_name, extracted_data)
    sentiment = analyze_promoter_sentiment(
        [article.get("title", "") for article in news.get("articles", [])],
        payload.company_name,
        payload.promoter_name,
    )

    errors = [
        *news.get("errors", []),
        *litigation.get("errors", []),
        *sector.get("errors", []),
    ]

    external_intelligence = {
        "news_articles_found": news.get("news_articles_found", 0),
        "negative_news_score": news.get("negative_news_score", 0.0),
        "litigation_cases": litigation.get("litigation_cases", 0),
        "high_risk_cases": litigation.get("high_risk_cases", 0),
        "sector": sector.get("sector", "General"),
        "sector_risk": sector.get("sector_risk", "Medium"),
        "promoter_sentiment": sentiment.get("promoter_sentiment", "Neutral"),
        "promoter_sentiment_confidence": sentiment.get("confidence", 0.0),
        "articles": news.get("articles", []),
        "sample_cases": litigation.get("sample_cases", []),
        "errors": [error for error in errors if error],
    }

    return {
        "financial_analysis": financial_analysis,
        "external_intelligence": external_intelligence,
    }
