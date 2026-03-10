from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from app.services.research.research_agent import build_research_intelligence


class ResearchAgentTests(unittest.TestCase):
    def test_build_research_intelligence_extracts_core_fields(self) -> None:
        fresh_ts = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat().replace("+00:00", "Z")
        old_ts = (datetime.now(timezone.utc) - timedelta(days=120)).isoformat().replace("+00:00", "Z")

        articles = [
            {
                "title": "Company faces court litigation and default concerns",
                "snippet": "A lawsuit and tribunal filing increased legal pressure.",
                "source": "NewsAPI",
                "url": "https://example.com/a",
                "published_at": fresh_ts,
            },
            {
                "title": "Sector growth and new orders improve demand",
                "snippet": "Investment pipeline signals moderate growth for industry.",
                "source": "Google CSE",
                "url": "https://example.com/b",
                "published_at": old_ts,
            },
        ]

        result = build_research_intelligence(
            company_name="Acme Infra Ltd",
            promoter_name="Promoter X",
            articles=articles,
            source_flags={"news_api": True, "serpapi": True, "google_search_api": True},
            errors=[],
        )

        self.assertIn("recent_news", result)
        self.assertIn("legal_risk", result)
        self.assertIn("sector_outlook", result)
        self.assertIn("market_sentiment", result)
        self.assertIn("research_features", result)
        self.assertIn("research_evidence", result)

        self.assertGreaterEqual(result["negative_news_score"], 0.0)
        self.assertLessEqual(result["negative_news_score"], 1.0)
        self.assertGreaterEqual(result["research_features"]["sector_growth_signal"], 0.0)
        self.assertLessEqual(result["research_features"]["sector_growth_signal"], 1.0)

    def test_recent_articles_have_higher_weight_than_stale_articles(self) -> None:
        fresh_ts = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat().replace("+00:00", "Z")
        stale_ts = (datetime.now(timezone.utc) - timedelta(days=180)).isoformat().replace("+00:00", "Z")

        articles = [
            {
                "title": "Fresh negative update with lawsuit default",
                "snippet": "court default litigation",
                "source": "NewsAPI",
                "url": "https://example.com/fresh",
                "published_at": fresh_ts,
            },
            {
                "title": "Old negative update with lawsuit default",
                "snippet": "court default litigation",
                "source": "NewsAPI",
                "url": "https://example.com/stale",
                "published_at": stale_ts,
            },
        ]

        result = build_research_intelligence(
            company_name="Acme Infra Ltd",
            promoter_name=None,
            articles=articles,
            source_flags={"news_api": True, "serpapi": False, "google_search_api": False},
            errors=[],
        )

        evidence = result["research_evidence"]["articles"]
        self.assertGreaterEqual(len(evidence), 2)
        self.assertGreater(evidence[0]["weight"], evidence[1]["weight"])


if __name__ == "__main__":
    unittest.main()
