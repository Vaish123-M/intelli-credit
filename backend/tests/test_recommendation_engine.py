from __future__ import annotations

import unittest

from app.services.ml.recommendation_engine import build_credit_recommendation


class RecommendationEngineTests(unittest.TestCase):
    def test_approve_threshold(self) -> None:
        payload = build_credit_recommendation(
            financial_metrics={
                "debt_equity_ratio": 0.9,
                "ebitda_margin": 0.22,
                "revenue_growth": 0.12,
                "gst_mismatch": False,
            },
            risk_score=0.38,
            secondary_research_signals={
                "market_sentiment": "Positive",
                "research_features": {
                    "negative_news_signal": 0.18,
                    "litigation_signal": 0.05,
                    "sector_growth_signal": 0.72,
                },
            },
        )
        self.assertEqual(payload["decision"], "Approve")
        self.assertIn("Low debt-to-equity ratio", payload["reasoning"])
        self.assertIn("Strong EBITDA margin", payload["reasoning"])
        self.assertIn("Positive revenue growth", payload["reasoning"])

    def test_review_threshold(self) -> None:
        payload = build_credit_recommendation(
            financial_metrics={
                "debt_equity_ratio": 1.6,
                "ebitda_margin": 0.11,
                "revenue_growth": 0.01,
                "gst_mismatch": False,
            },
            risk_score=0.55,
            secondary_research_signals={"market_sentiment": "Neutral", "research_features": {}},
        )
        self.assertEqual(payload["decision"], "Review")

    def test_reject_threshold(self) -> None:
        payload = build_credit_recommendation(
            financial_metrics={
                "debt_equity_ratio": 2.6,
                "ebitda_margin": 0.07,
                "revenue_growth": -0.06,
                "gst_mismatch": True,
            },
            risk_score=0.81,
            secondary_research_signals={
                "market_sentiment": "Negative",
                "research_features": {
                    "negative_news_signal": 0.82,
                    "litigation_signal": 0.77,
                    "sector_growth_signal": 0.32,
                },
            },
        )
        self.assertEqual(payload["decision"], "Reject")
        self.assertIn("High debt-to-equity ratio", payload["reasoning"])
        self.assertIn("Weak EBITDA margin", payload["reasoning"])
        self.assertIn("Recent negative news flow detected", payload["reasoning"])


if __name__ == "__main__":
    unittest.main()
