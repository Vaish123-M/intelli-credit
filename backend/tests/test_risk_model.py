from __future__ import annotations

from app.services.ml.recommendation_engine import MODEL_ARTIFACTS, build_credit_recommendation


def test_trained_risk_model_exposes_benchmark_metadata() -> None:
    assert MODEL_ARTIFACTS.model_version
    assert MODEL_ARTIFACTS.benchmark.get("accuracy", 0) >= 0.7
    assert MODEL_ARTIFACTS.benchmark.get("roc_auc", 0) >= 0.7


def test_risk_model_changes_with_input_profile() -> None:
    strong_profile = build_credit_recommendation(
        financial_metrics={
            "debt_equity_ratio": 0.8,
            "ebitda_margin": 0.24,
            "revenue_growth": 0.12,
            "gst_mismatch": False,
        },
        risk_score=None,
        secondary_research_signals={
            "market_sentiment": "Positive",
            "research_features": {
                "negative_news_signal": 0.08,
                "litigation_signal": 0.0,
                "sector_growth_signal": 0.8,
                "market_sentiment_signal": 0.2,
            },
        },
    )

    weak_profile = build_credit_recommendation(
        financial_metrics={
            "debt_equity_ratio": 2.9,
            "ebitda_margin": 0.05,
            "revenue_growth": -0.1,
            "gst_mismatch": True,
        },
        risk_score=None,
        secondary_research_signals={
            "market_sentiment": "Negative",
            "research_features": {
                "negative_news_signal": 0.82,
                "litigation_signal": 0.68,
                "sector_growth_signal": 0.28,
                "market_sentiment_signal": 0.88,
            },
        },
    )

    assert strong_profile["decision"] != weak_profile["decision"]
    assert strong_profile["risk_score"] < weak_profile["risk_score"]
    assert strong_profile["feature_contributions"]
    assert strong_profile["feature_contributions"][0]["feature"]