from __future__ import annotations

from typing import Any

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except Exception:  # noqa: BLE001
    SentimentIntensityAnalyzer = None  # type: ignore[assignment]

POSITIVE_WORDS = {"growth", "profit", "strong", "expands", "record", "wins", "improves"}
NEGATIVE_WORDS = {"fraud", "loss", "decline", "probe", "raid", "default", "penalty", "lawsuit"}


def _fallback_compound(text: str) -> float:
    text_lower = text.lower()
    pos = sum(1 for token in POSITIVE_WORDS if token in text_lower)
    neg = sum(1 for token in NEGATIVE_WORDS if token in text_lower)
    if pos == 0 and neg == 0:
        return 0.0
    return (pos - neg) / (pos + neg)


def analyze_promoter_sentiment(
    headlines: list[str],
    company_name: str,
    promoter_name: str | None = None,
) -> dict[str, Any]:
    analyzer = SentimentIntensityAnalyzer() if SentimentIntensityAnalyzer else None

    sentiment_pool = [headline for headline in headlines if headline]
    if not sentiment_pool:
        sentiment_pool = [company_name]
        if promoter_name:
            sentiment_pool.append(promoter_name)

    scores: list[float] = []
    for text in sentiment_pool:
        if analyzer:
            score = analyzer.polarity_scores(text).get("compound", 0.0)
        else:
            score = _fallback_compound(text)
        scores.append(float(score))

    avg_score = sum(scores) / len(scores)

    if avg_score <= -0.2:
        label = "Negative"
    elif avg_score >= 0.2:
        label = "Positive"
    else:
        label = "Neutral"

    return {
        "promoter_sentiment": label,
        "confidence": round(abs(avg_score), 2),
        "sentiment_score": round(avg_score, 3),
    }
