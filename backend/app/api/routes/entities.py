from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.services.audit_store import record_audit_event


router = APIRouter(tags=["entities"])


class EntityOnboardRequest(BaseModel):
    company_name: str
    cin: str
    pan: str
    sector: str
    annual_turnover: float
    loan_type: str
    loan_amount: float
    loan_tenure: str
    interest_rate: float


class SchemaMappingRequest(BaseModel):
    entity_id: str
    mappings: list[dict[str, Any]] = Field(default_factory=list)
    schema_definition: list[dict[str, str]] = Field(default_factory=list)


def _state(request: Request) -> dict[str, Any]:
    return request.app.state.app_state


def _helpers(request: Request) -> dict[str, Any]:
    return request.app.state.entity_helpers


@router.post("/entity-onboard")
def entity_onboard(payload: EntityOnboardRequest, request: Request) -> dict[str, Any]:
    state = _state(request)
    helpers = _helpers(request)
    entity_id = f"ent_{uuid4().hex[:12]}"
    entity_record = {
        "entity_id": entity_id,
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "company_name": payload.company_name,
        "cin": payload.cin,
        "pan": payload.pan,
        "sector": payload.sector,
        "annual_turnover": payload.annual_turnover,
        "loan_type": payload.loan_type,
        "loan_amount": payload.loan_amount,
        "loan_tenure": payload.loan_tenure,
        "interest_rate": payload.interest_rate,
        "uploaded_files": [],
        "extracted_data": [],
        "analysis": None,
        "research": None,
        "research_history": [],
        "classifications": [],
        "schema_mapping": helpers["build_schema_mapping"](
            detected_fields=[],
            schema_definition=helpers["default_schema_fields"],
        ),
    }

    state.setdefault("entities", {})[entity_id] = entity_record
    state["current_entity_id"] = entity_id
    request.app.state.persist_state()
    record_audit_event(
        "entity_onboarded",
        {
            "company_name": payload.company_name,
            "sector": payload.sector,
            "loan_type": payload.loan_type,
            "loan_amount": payload.loan_amount,
        },
        entity_id=entity_id,
        company_name=payload.company_name,
    )
    return {
        "entity_id": entity_id,
        "entity": entity_record,
        "message": "Entity onboarded successfully.",
    }


@router.get("/schema-definition")
def schema_definition(request: Request, entity_id: str | None = None) -> dict[str, Any]:
    helpers = _helpers(request)
    resolved_entity_id = helpers["resolve_entity_id"](entity_id)
    if not resolved_entity_id:
        return {"schema_definition": helpers["default_schema_fields"]}

    entity_bucket = helpers["get_entity_bucket"](resolved_entity_id)
    return {
        "entity_id": resolved_entity_id,
        "schema_definition": helpers["get_entity_schema_definition"](entity_bucket),
    }


@router.post("/schema-mapping/update")
def update_schema_mapping(payload: SchemaMappingRequest, request: Request) -> dict[str, Any]:
    state = _state(request)
    helpers = _helpers(request)
    resolved_entity_id = helpers["resolve_entity_id"](payload.entity_id)
    if not resolved_entity_id:
        raise HTTPException(status_code=400, detail="entity_id is required")

    entity_bucket = helpers["get_entity_bucket"](resolved_entity_id)
    detected_fields = [
        field
        for item in entity_bucket.get("extracted_data", [])
        for field in item.get("schema_detected_fields", [])
    ]
    manual_map = {
        str(item.get("detected_field")): str(item.get("system_field"))
        for item in payload.mappings
        if item.get("detected_field") and item.get("system_field")
    }
    schema_definition = payload.schema_definition or helpers["get_entity_schema_definition"](entity_bucket)
    schema_payload = helpers["build_schema_mapping"](
        detected_fields,
        manual_map,
        schema_definition,
    )
    entity_bucket["schema_mapping"] = schema_payload
    state["current_entity_id"] = resolved_entity_id
    request.app.state.persist_state()
    return {"entity_id": resolved_entity_id, **schema_payload}
