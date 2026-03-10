from __future__ import annotations

import unittest

from app.services.cam.final_report import build_final_report_markdown


class FinalReportGeneratorTests(unittest.TestCase):
    def test_markdown_contains_all_required_sections(self) -> None:
        markdown = build_final_report_markdown(
            company_overview={
                "company_name": "Acme Infra Ltd",
                "cin": "L12345",
                "pan": "ABCDE1234F",
                "sector": "Infrastructure",
                "annual_turnover": 125000000.0,
            },
            loan_details={
                "loan_type": "Working Capital",
                "loan_amount": 25000000.0,
                "loan_tenure": "36 months",
                "interest_rate": "12.5%",
            },
            financial_metrics={
                "revenue": 125000000.0,
                "ebitda": 18000000.0,
                "debt": 42000000.0,
                "equity": 56000000.0,
                "debt_equity_ratio": 0.75,
                "ebitda_margin": 0.144,
                "revenue_growth": 0.09,
            },
            risk_decision={
                "risk_score": 0.38,
                "risk_category": "Low Risk",
                "loan_decision": "Approve",
                "decision_status": "Approved",
                "loan_limit": "INR 1,50,00,000",
                "interest_rate": "11.50%",
                "reasoning": ["Low debt-to-equity ratio", "Positive revenue growth"],
                "top_risk_factors": ["No major adverse signals"],
            },
            secondary_research={
                "market_sentiment": "Positive",
                "legal_risk": "No major litigation found",
                "sector_outlook": "Moderate growth expected",
                "recent_news": ["Company expands manufacturing capacity"],
            },
            swot_analysis={
                "strengths": ["Positive revenue growth"],
                "weaknesses": ["Moderate leverage"],
                "opportunities": ["Growing sector demand"],
                "threats": ["Raw material price volatility"],
            },
        )

        self.assertIn("## 1. Company Overview", markdown)
        self.assertIn("## 2. Loan Details", markdown)
        self.assertIn("## 3. Extracted Financial Metrics", markdown)
        self.assertIn("## 4. Risk Score & Category", markdown)
        self.assertIn("## 5. Secondary Research Summary", markdown)
        self.assertIn("## 6. SWOT Analysis", markdown)
        self.assertIn("## 7. Credit Recommendation", markdown)
        self.assertIn("## 8. Key Risk Signals", markdown)


if __name__ == "__main__":
    unittest.main()
