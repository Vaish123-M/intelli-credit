from __future__ import annotations

import unittest

from app.services.ml.swot_generator import generate_swot_analysis


class SWOTGeneratorTests(unittest.TestCase):
    def test_swot_contains_expected_buckets(self) -> None:
        swot = generate_swot_analysis(
            financial_metrics={
                "debt_equity_ratio": 0.95,
                "ebitda_margin": 0.18,
                "revenue_growth": 0.12,
                "bank_cashflow": 500000.0,
                "gst_mismatch": False,
            },
            risk_analysis={
                "risk_score": 0.34,
                "loan_decision": "Approve",
            },
            secondary_research_signals={
                "market_sentiment": "Positive",
                "sector_outlook": "Strong growth expected",
                "research_features": {
                    "negative_news_signal": 0.12,
                    "litigation_signal": 0.05,
                    "sector_growth_signal": 0.7,
                },
            },
        )

        self.assertIn("strengths", swot)
        self.assertIn("weaknesses", swot)
        self.assertIn("opportunities", swot)
        self.assertIn("threats", swot)

        self.assertTrue(any("High EBITDA margin" in item for item in swot["strengths"]))
        self.assertTrue(any("Positive revenue growth" in item for item in swot["strengths"]))
        self.assertTrue(any("Growing sector demand" in item for item in swot["opportunities"]))

    def test_swot_threats_for_high_risk_profile(self) -> None:
        swot = generate_swot_analysis(
            financial_metrics={
                "debt_equity_ratio": 2.7,
                "ebitda_margin": 0.07,
                "revenue_growth": -0.04,
                "bank_cashflow": -10000.0,
                "gst_mismatch": True,
            },
            risk_analysis={
                "risk_score": 0.84,
                "loan_decision": "Reject",
            },
            secondary_research_signals={
                "market_sentiment": "Negative",
                "sector_outlook": "Weak growth outlook",
                "research_features": {
                    "negative_news_signal": 0.76,
                    "litigation_signal": 0.58,
                    "sector_growth_signal": 0.32,
                },
            },
        )

        self.assertTrue(any("High leverage" in item for item in swot["weaknesses"]))
        self.assertTrue(any("Adverse media coverage risk" in item for item in swot["threats"]))
        self.assertTrue(any("Elevated default risk profile" in item for item in swot["threats"]))


if __name__ == "__main__":
    unittest.main()
