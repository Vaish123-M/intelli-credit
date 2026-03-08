from __future__ import annotations

from typing import Any

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) IntelliCreditBot/1.0"
NEGATIVE_KEYWORDS = {
    "fraud",
    "investigation",
    "raid",
    "default",
    "scam",
    "lawsuit",
    "penalty",
    "arrest",
    "npa",
    "insolvency",
    "loss",
}


def _search_duckduckgo(query: str, max_results: int = 5) -> list[dict[str, str]]:
    url = "https://duckduckgo.com/html/"
    response = requests.get(
        url,
        params={"q": query},
        headers={"User-Agent": USER_AGENT},
        timeout=8,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    rows: list[dict[str, str]] = []
    for result in soup.select(".result"):
        anchor = result.select_one(".result__a")
        snippet = result.select_one(".result__snippet")
        if not anchor:
            continue
        title = anchor.get_text(" ", strip=True)
        link = anchor.get("href", "")
        summary = snippet.get_text(" ", strip=True) if snippet else ""
        rows.append({"title": title, "link": link, "summary": summary})
        if len(rows) >= max_results:
            break

    return rows


def _negative_article_score(title: str, summary: str) -> float:
    text = f"{title} {summary}".lower()
    matches = sum(1 for keyword in NEGATIVE_KEYWORDS if keyword in text)
    if matches == 0:
        return 0.0
    return min(1.0, matches / 3.0)


def fetch_news_intelligence(company_name: str, promoter_name: str | None = None) -> dict[str, Any]:
    search_queries = [
        company_name,
        f"{company_name} fraud investigation",
        f"{company_name} business performance",
    ]
    if promoter_name:
        search_queries.append(f"{promoter_name} {company_name} news")

    articles: list[dict[str, str]] = []
    dedupe_keys: set[str] = set()
    errors: list[str] = []

    for query in search_queries:
        try:
            for row in _search_duckduckgo(query):
                key = row["title"].strip().lower()
                if not key or key in dedupe_keys:
                    continue
                dedupe_keys.add(key)
                articles.append(row)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"News lookup failed for '{query}': {exc}")

    article_count = len(articles)
    if article_count == 0:
        return {
            "news_articles_found": 0,
            "negative_news_score": 0.0,
            "articles": [],
            "errors": errors,
        }

    negative_total = sum(_negative_article_score(article["title"], article.get("summary", "")) for article in articles)
    negative_news_score = round(min(1.0, negative_total / article_count), 2)

    return {
        "news_articles_found": article_count,
        "negative_news_score": negative_news_score,
        "articles": articles[:8],
        "errors": errors,
    }
