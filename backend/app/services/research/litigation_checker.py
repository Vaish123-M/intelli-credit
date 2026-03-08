from __future__ import annotations

from typing import Any

from app.services.research.news_agent import fetch_news_intelligence

LITIGATION_KEYWORDS = {"litigation", "court", "tribunal", "case", "lawsuit", "petition", "dispute"}
HIGH_RISK_KEYWORDS = {
    "fraud",
    "money laundering",
    "sebi",
    "ed",
    "cbi",
    "sfio",
    "insolvency",
    "nclt",
    "criminal",
}


def check_litigation(company_name: str) -> dict[str, Any]:
    # Reuse news lookup with litigation-focused query to avoid duplicated scraping logic.
    payload = fetch_news_intelligence(f"{company_name} litigation court case")
    articles = payload.get("articles", [])

    litigation_cases = 0
    high_risk_cases = 0
    sample_cases: list[str] = []

    for article in articles:
        title = article.get("title", "")
        summary = article.get("summary", "")
        text = f"{title} {summary}".lower()

        if any(keyword in text for keyword in LITIGATION_KEYWORDS):
            litigation_cases += 1
            sample_cases.append(title)

            if any(keyword in text for keyword in HIGH_RISK_KEYWORDS):
                high_risk_cases += 1

    return {
        "litigation_cases": litigation_cases,
        "high_risk_cases": high_risk_cases,
        "sample_cases": sample_cases[:5],
        "errors": payload.get("errors", []),
    }
