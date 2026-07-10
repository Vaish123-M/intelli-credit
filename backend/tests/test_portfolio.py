from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app, _default_state, _persist_state, state


def _reset_state() -> None:
    state.clear()
    state.update(_default_state())
    _persist_state()


def _create_sample_deal(company_name: str, risk_score: float) -> dict:
    """Helper to create a sample deal."""
    return {
        "company_name": company_name,
        "risk_score": risk_score,
        "risk_category": "High Risk" if risk_score >= 0.6 else ("Medium Risk" if risk_score >= 0.4 else "Low Risk"),
        "loan_limit": "INR 1,00,00,000",
        "interest_rate": "12.5%",
        "loan_decision": "Review" if risk_score >= 0.6 else "Approve",
        "timestamp": "2024-01-01T00:00:00Z",
    }


def _create_sample_entity(company_name: str) -> dict:
    """Helper to create a sample entity."""
    return {
        "company_name": company_name,
        "sector": "Technology",
        "annual_turnover": 10000000,
        "loan_type": "Working Capital",
        "loan_amount": 5000000,
        "uploaded_files": [],
        "classifications": [],
    }


def test_portfolio_summary_empty():
    """Test portfolio summary with no data."""
    _reset_state()
    client = TestClient(app)
    
    response = client.get("/portfolio/summary")
    
    assert response.status_code == 200
    data = response.json()
    assert data["companies_analyzed"] == 0
    assert data["total_exposure"] == 0
    assert data["low_risk"] == 0
    assert data["medium_risk"] == 0
    assert data["high_risk"] == 0


def test_portfolio_summary_with_deals():
    """Test portfolio summary with deals."""
    _reset_state()
    client = TestClient(app)
    
    # Add sample deals
    state["deals"] = [
        _create_sample_deal("Company A", 0.3),
        _create_sample_deal("Company B", 0.5),
        _create_sample_deal("Company C", 0.7),
    ]
    _persist_state()
    
    response = client.get("/portfolio/summary")
    
    assert response.status_code == 200
    data = response.json()
    assert data["companies_analyzed"] == 3
    assert data["low_risk"] == 1
    assert data["medium_risk"] == 1
    assert data["high_risk"] == 1
    assert data["total_exposure"] > 0


def test_portfolio_alerts_no_alerts():
    """Test portfolio alerts with no high-risk companies."""
    _reset_state()
    client = TestClient(app)
    
    # Add low-risk deals only
    state["deals"] = [
        _create_sample_deal("Company A", 0.3),
        _create_sample_deal("Company B", 0.35),
    ]
    state["entities"] = {}
    _persist_state()
    
    response = client.get("/portfolio/alerts")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_portfolio_alerts_with_high_risk():
    """Test portfolio alerts with high-risk companies."""
    _reset_state()
    client = TestClient(app)
    
    # Add high-risk deals
    state["deals"] = [
        _create_sample_deal("Company A", 0.7),
        _create_sample_deal("Company B", 0.8),
    ]
    state["entities"] = {}
    _persist_state()
    
    response = client.get("/portfolio/alerts")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any("High risk" in alert for alert in data)


def test_portfolio_alerts_with_rejected():
    """Test portfolio alerts with rejected deals."""
    _reset_state()
    client = TestClient(app)
    
    # Add rejected deal
    deal = _create_sample_deal("Company A", 0.8)
    deal["loan_decision"] = "Reject"
    state["deals"] = [deal]
    state["entities"] = {}
    _persist_state()
    
    response = client.get("/portfolio/alerts")
    
    assert response.status_code == 200
    data = response.json()
    assert any("rejected" in alert.lower() for alert in data)


def test_portfolio_alerts_missing_documents():
    """Test portfolio alerts for missing required documents."""
    _reset_state()
    client = TestClient(app)
    
    # Add entity with missing documents
    state["entities"] = {
        "ent_123": {
            "company_name": "Company A",
            "uploaded_files": [{"name": "file1.pdf"}],
            "classifications": [],
        }
    }
    state["deals"] = []
    _persist_state()
    
    response = client.get("/portfolio/alerts")
    
    assert response.status_code == 200
    data = response.json()
    assert any("Missing required document" in alert for alert in data)


def test_portfolio_companies_empty():
    """Test portfolio companies with no entities."""
    _reset_state()
    client = TestClient(app)
    
    response = client.get("/portfolio/companies")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_portfolio_companies_with_entities():
    """Test portfolio companies with entities."""
    _reset_state()
    client = TestClient(app)
    
    # Add entities and deals
    state["entities"] = {
        "ent_123": _create_sample_entity("Company A"),
        "ent_456": _create_sample_entity("Company B"),
    }
    state["deals"] = [
        _create_sample_deal("Company A", 0.3),
        _create_sample_deal("Company B", 0.5),
    ]
    _persist_state()
    
    response = client.get("/portfolio/companies")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(c["company_name"] == "Company A" for c in data)
    assert any(c["company_name"] == "Company B" for c in data)


def test_portfolio_high_risk_empty():
    """Test portfolio high-risk with no data."""
    _reset_state()
    client = TestClient(app)
    
    response = client.get("/portfolio/high-risk")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_portfolio_high_risk_with_threshold():
    """Test portfolio high-risk filtering by threshold."""
    _reset_state()
    client = TestClient(app)
    
    # Add mixed risk deals
    state["entities"] = {
        "ent_123": _create_sample_entity("Company A"),
        "ent_456": _create_sample_entity("Company B"),
        "ent_789": _create_sample_entity("Company C"),
    }
    state["deals"] = [
        _create_sample_deal("Company A", 0.3),
        _create_sample_deal("Company B", 0.7),
        _create_sample_deal("Company C", 0.8),
    ]
    _persist_state()
    
    response = client.get("/portfolio/high-risk")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Only B and C should be high-risk
    assert all(c["risk_score"] >= 0.6 for c in data)
    # Should be sorted by risk score descending
    assert data[0]["risk_score"] >= data[1]["risk_score"]


def test_portfolio_high_risk_custom_threshold():
    """Test portfolio high-risk with custom threshold via env var."""
    import os
    original_threshold = os.environ.get("HIGH_RISK_THRESHOLD")
    
    try:
        os.environ["HIGH_RISK_THRESHOLD"] = "0.8"
        _reset_state()
        client = TestClient(app)
        
        state["entities"] = {
            "ent_123": _create_sample_entity("Company A"),
        }
        state["deals"] = [
            _create_sample_deal("Company A", 0.7),
        ]
        _persist_state()
        
        response = client.get("/portfolio/high-risk")
        
        assert response.status_code == 200
        data = response.json()
        # With threshold 0.8, 0.7 should not be high-risk
        assert len(data) == 0
    finally:
        if original_threshold:
            os.environ["HIGH_RISK_THRESHOLD"] = original_threshold
        else:
            os.environ.pop("HIGH_RISK_THRESHOLD", None)
