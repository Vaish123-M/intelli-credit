from __future__ import annotations

from typing import Any

from app.services.research.news_agent import fetch_news_intelligence

SECTOR_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Textiles": ("textile", "fabric", "garment", "yarn", "spinning"),
    "Real Estate": ("real estate", "property", "housing", "construction", "developer"),
    "Manufacturing": ("manufacturing", "plant", "factory", "production", "industrial"),
    "IT Services": ("software", "it services", "technology", "digital", "saas"),
}

SECTOR_RISK_BASELINE: dict[str, str] = {
    "Textiles": "Medium",
    "Real Estate": "High",
    "Manufacturing": "Medium",
    "IT Services": "Low",
    "General": "Medium",
}


def _flatten_extracted_text(extracted_data: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for item in extracted_data:
        chunks.append(str(item.get("filename", "")))
        chunks.append(str(item.get("category", "")))
        chunks.append(str(item.get("text_preview", "")))
        chunks.extend(str(column) for column in item.get("columns", []) or [])
    return " ".join(chunks).lower()


def _detect_sector(company_name: str, extracted_data: list[dict[str, Any]]) -> str:
    corpus = f"{company_name} {_flatten_extracted_text(extracted_data)}".lower()
    best_sector = "General"
    best_score = 0

    for sector, keywords in SECTOR_KEYWORDS.items():
        score = sum(corpus.count(keyword) for keyword in keywords)
        if score > best_score:
            best_sector = sector
            best_score = score

    return best_sector


def analyze_sector_risk(company_name: str, extracted_data: list[dict[str, Any]]) -> dict[str, Any]:
    sector = _detect_sector(company_name, extracted_data)
    sector_risk = SECTOR_RISK_BASELINE.get(sector, "Medium")

    errors: list[str] = []
    try:
        risk_news = fetch_news_intelligence(f"{sector} sector slowdown India")
        negative_score = float(risk_news.get("negative_news_score", 0.0) or 0.0)
        if negative_score >= 0.6:
            sector_risk = "High"
        elif negative_score <= 0.2 and sector_risk == "Medium":
            sector_risk = "Low"
        errors.extend(risk_news.get("errors", []))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"Sector risk lookup failed: {exc}")

    return {
        "sector": sector,
        "sector_risk": sector_risk,
        "errors": errors,
    }
