from __future__ import annotations

import io
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app, _default_state, _persist_state, state


REQUIRED_TYPES = [
    "ALM (Asset Liability Management)",
    "Shareholding Pattern",
    "Borrowing Profile",
    "Annual Report",
    "Portfolio Cuts / Performance Data",
]


def _sample_csv() -> bytes:
    return (
        "metric,2023,2024\n"
        "Revenue,1000000,1250000\n"
        "EBITDA,180000,210000\n"
        "Borrowings,450000,420000\n"
        "Equity,520000,560000\n"
    ).encode("utf-8")


def _reset_state() -> None:
    state.clear()
    state.update(_default_state())
    _persist_state()


def test_full_credit_journey() -> None:
    _reset_state()
    client = TestClient(app)

    onboard_payload = {
        "company_name": "Acme Infra Ltd",
        "cin": "L12345",
        "pan": "ABCDE1234F",
        "sector": "Infrastructure",
        "annual_turnover": 125000000,
        "loan_type": "Working Capital",
        "loan_amount": 25000000,
        "loan_tenure": "36 months",
        "interest_rate": 12.5,
    }
    onboard = client.post("/entity-onboard", json=onboard_payload)
    assert onboard.status_code == 200
    entity_id = onboard.json()["entity_id"]

    filenames = [
        "alm_statement.csv",
        "shareholding_pattern.csv",
        "borrowing_profile.csv",
        "annual_report_financials.csv",
        "portfolio_performance.csv",
    ]

    classify_files = [("files", (name, io.BytesIO(_sample_csv()), "text/csv")) for name in filenames]
    classify = client.post("/classify-documents", data={"entity_id": entity_id}, files=classify_files)
    assert classify.status_code == 200
    assert len(classify.json().get("results", [])) == 5

    classifications = []
    for file_name, doc_type in zip(filenames, REQUIRED_TYPES):
        classifications.append(
            {
                "file_name": file_name,
                "predicted_type": doc_type,
                "detected_type": doc_type,
                "confidence": 0.95,
                "approved": True,
            }
        )

    upload_files = [("files", (name, io.BytesIO(_sample_csv()), "text/csv")) for name in filenames]
    upload = client.post(
        "/upload",
        data={"entity_id": entity_id, "classifications": json.dumps(classifications)},
        files=upload_files,
    )
    assert upload.status_code == 200
    upload_payload = upload.json()
    assert upload_payload["analysis"] is not None
    assert upload_payload.get("extraction_quality_summary", {}).get("files_processed") == 5

    schema_mapping = upload_payload["schema_mapping"]
    updated_schema = list(schema_mapping["schema_definition"]) + [{"key": "dscr", "label": "DSCR"}]
    map_resp = client.post(
        "/schema-mapping/update",
        json={
            "entity_id": entity_id,
            "mappings": schema_mapping["mappings"],
            "schema_definition": updated_schema,
        },
    )
    assert map_resp.status_code == 200
    map_payload = map_resp.json()
    assert any(field.get("label") == "DSCR" for field in map_payload.get("schema_definition", []))

    research = client.post(
        "/research",
        json={"company_name": "Acme Infra Ltd", "promoter_name": "Promoter X", "entity_id": entity_id},
    )
    assert research.status_code == 200
    research_payload = research.json()

    risk = client.post(
        "/risk-score",
        json={
            "company_name": "Acme Infra Ltd",
            "financial_analysis": upload_payload["analysis"],
            "external_intelligence": research_payload["external_intelligence"],
        },
    )
    assert risk.status_code == 200
    risk_payload = risk.json()
    assert "loan_decision" in risk_payload

    final_report = client.post(
        "/generate-final-report",
        json={
            "company_name": "Acme Infra Ltd",
            "entity_id": entity_id,
            "financial_analysis": upload_payload["analysis"],
            "external_intelligence": research_payload["external_intelligence"],
            "risk_decision": risk_payload,
        },
    )
    assert final_report.status_code == 200
    report_url = final_report.json().get("final_report_url")
    assert report_url

    file_name = Path(report_url).name
    download = client.get(f"/downloads/{file_name}")
    assert download.status_code == 200
