from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus
from urllib.request import urlopen


NEGATIVE_NEWS_KEYWORDS = [
    "fraud",
    "default",
    "insolvency",
    "bankruptcy",
    "downgrade",
    "probe",
    "penalty",
    "shutdown",
    "loss",
    "layoff",
    "delay",
    "non-compliance",
]

LITIGATION_KEYWORDS = [
    "court",
    "litigation",
    "lawsuit",
    "legal notice",
    "tribunal",
    "arbitration",
    "nclt",
    "nclat",
    "suit filed",
    "summons",
]

SECTOR_GROWTH_KEYWORDS = [
    "growth",
    "demand rise",
    "capacity expansion",
    "new orders",
    "investment",
    "policy support",
    "moderate growth",
    "strong outlook",
]

SECTOR_STRESS_KEYWORDS = [
    "slowdown",
    "headwinds",
    "weak demand",
    "cost pressure",
    "contraction",
    "decline",
    "margin pressure",
]


@dataclass
class ResearchSignalCounts:
    negative_news_mentions: float = 0.0
    litigation_mentions: float = 0.0
    sector_growth_mentions: float = 0.0
    sector_stress_mentions: float = 0.0


def _safe_get(url: str, timeout: int = 8) -> dict[str, Any]:
    with urlopen(url, timeout=timeout) as response:  # nosec: B310 - URLs are trusted API hosts assembled server-side.
        payload = response.read().decode("utf-8", errors="replace")
    return json.loads(payload or "{}")


def _extract_sector_from_name(company_name: str) -> str:
    n = company_name.lower()
    if any(keyword in n for keyword in ["infra", "construction", "steel", "cement"]):
        return "Infrastructure"
    if any(keyword in n for keyword in ["pharma", "health", "biotech"]):
        return "Pharma"
    if any(keyword in n for keyword in ["textile", "garment", "apparel"]):
        return "Textiles"
    if any(keyword in n for keyword in ["it", "software", "tech", "digital"]):
        return "Technology"
    if any(keyword in n for keyword in ["auto", "automobile", "mobility", "ev"]):
        return "Automotive"
    return "General"


def _collect_newsapi_articles(company_name: str, news_api_key: str) -> list[dict[str, str]]:
    query = quote_plus(f'"{company_name}"')
    url = (
        "https://newsapi.org/v2/everything"
        f"?q={query}&language=en&sortBy=publishedAt&pageSize=8&apiKey={quote_plus(news_api_key)}"
    )
    payload = _safe_get(url)
    articles = payload.get("articles") or []
    normalized: list[dict[str, str]] = []
    for article in articles:
        normalized.append(
            {
                "title": str(article.get("title") or "").strip(),
                "snippet": str(article.get("description") or "").strip(),
                "source": str((article.get("source") or {}).get("name") or "NewsAPI"),
                "url": str(article.get("url") or "").strip(),
                "published_at": str(article.get("publishedAt") or ""),
            }
        )
    return normalized


def _collect_serpapi_results(query: str, serpapi_key: str) -> list[dict[str, str]]:
    url = (
        "https://serpapi.com/search.json"
        f"?engine=google&q={quote_plus(query)}&api_key={quote_plus(serpapi_key)}&num=8"
    )
    payload = _safe_get(url)
    items = payload.get("organic_results") or []
    normalized: list[dict[str, str]] = []
    for item in items:
        normalized.append(
            {
                "title": str(item.get("title") or "").strip(),
                "snippet": str(item.get("snippet") or "").strip(),
                "source": "SerpAPI",
                "url": str(item.get("link") or "").strip(),
                "published_at": "",
            }
        )
    return normalized


def _collect_google_cse_results(query: str, google_api_key: str, google_cse_id: str) -> list[dict[str, str]]:
    url = (
        "https://www.googleapis.com/customsearch/v1"
        f"?key={quote_plus(google_api_key)}&cx={quote_plus(google_cse_id)}"
        f"&q={quote_plus(query)}&num=8"
    )
    payload = _safe_get(url)
    items = payload.get("items") or []
    normalized: list[dict[str, str]] = []
    for item in items:
        normalized.append(
            {
                "title": str(item.get("title") or "").strip(),
                "snippet": str(item.get("snippet") or "").strip(),
                "source": "Google CSE",
                "url": str(item.get("link") or "").strip(),
                "published_at": "",
            }
        )
    return normalized


def _normalize_recent_news(articles: list[dict[str, str]], limit: int = 5) -> list[str]:
    items: list[str] = []
    seen: set[str] = set()
    for article in articles:
        title = str(article.get("title") or "").strip()
        if not title:
            continue
        key = re.sub(r"\s+", " ", title.lower())
        if key in seen:
            continue
        seen.add(key)
        items.append(title)
        if len(items) >= limit:
            break
    return items


def _count_keyword_mentions(text: str, keywords: list[str]) -> int:
    content = text.lower()
    return sum(1 for keyword in keywords if keyword in content)


def _parse_published_at(value: str) -> datetime | None:
    if not value:
        return None
    candidate = value.strip()
    if not candidate:
        return None
    try:
        if candidate.endswith("Z"):
            candidate = candidate[:-1] + "+00:00"
        return datetime.fromisoformat(candidate).astimezone(timezone.utc)
    except ValueError:
        return None


def _source_weight(source: str) -> float:
    s = source.lower()
    if "synthetic" in s:
        return 0.6
    if "newsapi" in s:
        return 1.0
    if "google cse" in s or "serpapi" in s:
        return 0.9
    return 0.85


def _recency_weight(published_at: str) -> float:
    parsed = _parse_published_at(published_at)
    if parsed is None:
        return 0.6
    age_days = max((datetime.now(timezone.utc) - parsed).days, 0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 90:
        return 0.6
    return 0.45


def _article_weight(article: dict[str, str]) -> float:
    return _source_weight(str(article.get("source") or "")) * _recency_weight(str(article.get("published_at") or ""))


def _compute_signal_counts(articles: list[dict[str, str]]) -> ResearchSignalCounts:
    counts = ResearchSignalCounts()
    for article in articles:
        blob = f"{article.get('title', '')} {article.get('snippet', '')}".lower()
        weight = _article_weight(article)
        counts.negative_news_mentions += _count_keyword_mentions(blob, NEGATIVE_NEWS_KEYWORDS) * weight
        counts.litigation_mentions += _count_keyword_mentions(blob, LITIGATION_KEYWORDS) * weight
        counts.sector_growth_mentions += _count_keyword_mentions(blob, SECTOR_GROWTH_KEYWORDS) * weight
        counts.sector_stress_mentions += _count_keyword_mentions(blob, SECTOR_STRESS_KEYWORDS) * weight
    return counts


def _bounded(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _derive_sector_outlook(growth_mentions: int, stress_mentions: int) -> tuple[str, str]:
    delta = growth_mentions - stress_mentions
    if delta >= 2:
        return "Strong growth expected", "Low"
    if delta <= -2:
        return "Weak growth outlook", "High"
    return "Moderate growth expected", "Medium"


def build_research_intelligence(
    company_name: str,
    promoter_name: str | None,
    articles: list[dict[str, str]],
    source_flags: dict[str, bool],
    errors: list[str],
) -> dict[str, Any]:
    sector = _extract_sector_from_name(company_name)
    signal_counts = _compute_signal_counts(articles)
    sector_outlook, sector_risk = _derive_sector_outlook(
        int(round(signal_counts.sector_growth_mentions)),
        int(round(signal_counts.sector_stress_mentions)),
    )

    negative_news_score = _bounded(0.14 + signal_counts.negative_news_mentions * 0.09)
    litigation_risk_score = _bounded(signal_counts.litigation_mentions * 0.24)

    if signal_counts.litigation_mentions >= 2.5:
        legal_risk = "High litigation activity detected"
    elif signal_counts.litigation_mentions >= 0.8:
        legal_risk = "Some litigation mentions found"
    else:
        legal_risk = "No major litigation found"

    if negative_news_score >= 0.62 or litigation_risk_score >= 0.62:
        market_sentiment = "Negative"
    elif negative_news_score <= 0.3 and signal_counts.sector_growth_mentions >= signal_counts.sector_stress_mentions:
        market_sentiment = "Positive"
    else:
        market_sentiment = "Neutral"

    promoter_sentiment = "Negative" if market_sentiment == "Negative" else ("Positive" if market_sentiment == "Positive" else "Neutral")
    promoter_confidence = _bounded(0.55 + abs(0.5 - negative_news_score) * 0.5)

    recent_news = _normalize_recent_news(
        sorted(articles, key=lambda item: _article_weight(item), reverse=True)
    )

    research_features = {
        "negative_news_signal": round(negative_news_score, 4),
        "litigation_signal": round(litigation_risk_score, 4),
        "sector_growth_signal": round(_bounded(0.5 + (signal_counts.sector_growth_mentions - signal_counts.sector_stress_mentions) * 0.12), 4),
        "market_sentiment_signal": 0.25 if market_sentiment == "Positive" else (0.5 if market_sentiment == "Neutral" else 0.85),
    }

    evidence = [
        {
            "title": str(item.get("title") or ""),
            "snippet": str(item.get("snippet") or ""),
            "source": str(item.get("source") or ""),
            "url": str(item.get("url") or ""),
            "published_at": str(item.get("published_at") or ""),
            "weight": round(_article_weight(item), 4),
        }
        for item in sorted(articles, key=lambda itm: _article_weight(itm), reverse=True)[:20]
    ]

    return {
        "recent_news": recent_news,
        "legal_risk": legal_risk,
        "sector_outlook": sector_outlook,
        "market_sentiment": market_sentiment,
        "negative_news_score": round(negative_news_score, 4),
        "news_articles_found": len(articles),
        "litigation_cases": int(round(signal_counts.litigation_mentions)),
        "high_risk_cases": 1 if litigation_risk_score >= 0.6 else 0,
        "litigation_mentions": round(signal_counts.litigation_mentions, 4),
        "negative_news_mentions": round(signal_counts.negative_news_mentions, 4),
        "sector_growth_trend_mentions": round(signal_counts.sector_growth_mentions, 4),
        "sector_risk": sector_risk,
        "sector": sector,
        "promoter_sentiment": promoter_sentiment,
        "promoter_sentiment_confidence": round(promoter_confidence, 4),
        "promoter_name": promoter_name,
        "sources_used": source_flags,
        "research_features": research_features,
        "research_evidence": {
            "article_count": len(articles),
            "articles": evidence,
        },
        "errors": errors,
    }


def run_secondary_research(company_name: str, promoter_name: str | None = None) -> dict[str, Any]:
    company_name = (company_name or "").strip()
    promoter_name = (promoter_name or "").strip() or None
    sector = _extract_sector_from_name(company_name)

    news_api_key = os.getenv("NEWS_API_KEY", "").strip()
    serpapi_key = os.getenv("SERPAPI_KEY", "").strip()
    google_api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    google_cse_id = os.getenv("GOOGLE_CSE_ID", "").strip()

    errors: list[str] = []
    all_articles: list[dict[str, str]] = []

    if news_api_key:
        try:
            all_articles.extend(_collect_newsapi_articles(company_name, news_api_key))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"News API failed: {exc}")
    else:
        errors.append("News API key not configured")

    base_query = f"{company_name} legal case litigation sector trend market sentiment"
    if serpapi_key:
        try:
            all_articles.extend(_collect_serpapi_results(base_query, serpapi_key))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"SerpAPI failed: {exc}")
    else:
        errors.append("SerpAPI key not configured")

    if google_api_key and google_cse_id:
        try:
            all_articles.extend(_collect_google_cse_results(base_query, google_api_key, google_cse_id))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Google Search API failed: {exc}")
    else:
        errors.append("Google Search API key/cx not configured")

    if not all_articles:
        # Deterministic fallback keeps the workflow usable in local demos without API keys.
        all_articles = [
            {
                "title": f"{company_name} expands manufacturing capacity in core market",
                "snippet": "Sector participants expect moderate growth over the next 12 months.",
                "source": "Synthetic",
                "url": "",
                "published_at": "",
            },
            {
                "title": f"Analysts see stable demand for {sector} companies",
                "snippet": "No major litigation updates were highlighted in recent briefings.",
                "source": "Synthetic",
                "url": "",
                "published_at": "",
            },
        ]

    return build_research_intelligence(
        company_name=company_name,
        promoter_name=promoter_name,
        articles=all_articles,
        source_flags={
            "news_api": bool(news_api_key),
            "serpapi": bool(serpapi_key),
            "google_search_api": bool(google_api_key and google_cse_id),
        },
        errors=errors,
    )
