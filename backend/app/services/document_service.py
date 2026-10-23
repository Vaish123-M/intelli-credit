from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from fastapi import HTTPException, UploadFile


logger = logging.getLogger("intelli_credit.documents")


def analyze_documents(
    entity_id: str | None,
    *,
    state: dict[str, Any],
    resolve_entity_id: Callable[[str | None], str | None],
    get_entity_bucket: Callable[[str], dict[str, Any]],
    build_analysis: Callable[[list[dict[str, Any]]], dict[str, Any]],
    summarize_quality: Callable[[list[dict[str, Any]]], dict[str, Any]],
    persist_state: Callable[[], None],
) -> dict[str, Any]:
    resolved_entity_id = resolve_entity_id(entity_id)
    if resolved_entity_id:
        entity_bucket = get_entity_bucket(resolved_entity_id)
        extracted_data = entity_bucket.get("extracted_data", [])
    else:
        extracted_data = state.get("extracted_data", [])

    analysis = build_analysis(extracted_data)
    state["analysis"] = analysis
    if resolved_entity_id:
        entity_bucket["analysis"] = analysis
        state["current_entity_id"] = resolved_entity_id
        entity_bucket["extraction_quality_summary"] = summarize_quality(extracted_data)
    persist_state()
    return {"entity_id": resolved_entity_id, "analysis": analysis, "extracted_data": extracted_data}


def document_results(
    entity_id: str | None,
    *,
    state: dict[str, Any],
    resolve_entity_id: Callable[[str | None], str | None],
    get_entity_bucket: Callable[[str], dict[str, Any]],
    summarize_quality: Callable[[list[dict[str, Any]]], dict[str, Any]],
) -> dict[str, Any]:
    resolved_entity_id = resolve_entity_id(entity_id)
    if resolved_entity_id:
        entity_bucket = get_entity_bucket(resolved_entity_id)
        return {
            "entity_id": resolved_entity_id,
            "uploaded_files": entity_bucket.get("uploaded_files", []),
            "extracted_data": entity_bucket.get("extracted_data", []),
            "analysis": entity_bucket.get("analysis"),
            "extraction_quality_summary": entity_bucket.get("extraction_quality_summary"),
            "research": entity_bucket.get("research"),
            "research_history": entity_bucket.get("research_history", []),
            "schema_mapping": entity_bucket.get("schema_mapping"),
        }

    extracted_data = state.get("extracted_data", [])
    return {
        "entity_id": None,
        "uploaded_files": state.get("uploaded_files", []),
        "extracted_data": extracted_data,
        "analysis": state.get("analysis"),
        "extraction_quality_summary": summarize_quality(extracted_data),
        "research": state.get("research"),
        "research_history": [],
        "schema_mapping": None,
    }


async def classify_documents(
    entity_id: str,
    files: list[UploadFile],
    *,
    state: dict[str, Any],
    uploads_dir: Path,
    document_types: list[str],
    resolve_entity_id: Callable[[str | None], str | None],
    get_entity_bucket: Callable[[str], dict[str, Any]],
    validate_upload: Callable[[str, bytes], None],
    antivirus_scan: Callable[[str, bytes], None],
    sanitize_filename: Callable[[str], str],
    extract_text: Callable[[Path], tuple[str, dict[str, Any]]],
    extract_pdf_metrics: Callable[[Path], tuple[dict[str, int], Any, Any]],
    extract_csv_metrics: Callable[[Path], tuple[dict[str, int], Any, Any]],
    extract_text_metrics: Callable[[str, str], tuple[dict[str, int], Any, Any]],
    classify_file: Callable[[str, str, dict[str, int]], dict[str, Any]],
    persist_state: Callable[[], None],
) -> dict[str, Any]:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    resolved_entity_id = resolve_entity_id(entity_id)
    if not resolved_entity_id:
        raise HTTPException(
            status_code=400,
            detail="entity_id is required. Please complete onboarding first.",
        )

    entity_bucket = get_entity_bucket(resolved_entity_id)
    results: list[dict[str, Any]] = []

    for upload_file in files:
        safe_name = upload_file.filename or f"upload_{uuid4().hex[:12]}.bin"
        content = await upload_file.read()
        validate_upload(safe_name, content)
        antivirus_scan(safe_name, content)
        temp_path = uploads_dir / sanitize_filename(safe_name)
        temp_path.write_bytes(content)

        try:
            parsed_text, _ = extract_text(temp_path)
            if temp_path.suffix.lower() == ".pdf":
                table_metrics, _, _ = extract_pdf_metrics(temp_path)
            elif temp_path.suffix.lower() == ".csv":
                table_metrics, _, _ = extract_csv_metrics(temp_path)
            else:
                table_metrics, _, _ = extract_text_metrics(parsed_text, safe_name)
            results.append(classify_file(safe_name, parsed_text, table_metrics))
        except HTTPException:
            raise
        except Exception as error:  # noqa: BLE001
            logger.exception("Classification failed for file %s", safe_name)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to classify '{safe_name}': {error}",
            ) from error
        finally:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                logger.warning("Could not remove temp file %s", temp_path)

    entity_bucket["classifications"] = results
    state["current_entity_id"] = resolved_entity_id
    persist_state()

    return {
        "entity_id": resolved_entity_id,
        "results": results,
        "supported_types": document_types,
    }
