from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, File, Form, Request, UploadFile


router = APIRouter(tags=["documents"])


def _handler(request: Request, name: str) -> Callable[..., Any]:
    return request.app.state.document_handlers[name]


@router.post("/classify-documents")
async def classify_documents(
    request: Request,
    entity_id: str = Form(...),
    files: list[UploadFile] = File(...),
) -> dict[str, Any]:
    return await _handler(request, "classify_documents")(entity_id=entity_id, files=files)


@router.post("/upload")
async def upload(
    request: Request,
    entity_id: str = Form(...),
    files: list[UploadFile] = File(...),
    classifications: str | None = Form(None),
) -> dict[str, Any]:
    return await _handler(request, "upload")(
        entity_id=entity_id,
        files=files,
        classifications=classifications,
    )


@router.post("/analyze")
def analyze(request: Request, entity_id: str | None = None) -> dict[str, Any]:
    return _handler(request, "analyze")(entity_id=entity_id)


@router.get("/results")
def results(request: Request, entity_id: str | None = None) -> dict[str, Any]:
    return _handler(request, "results")(entity_id=entity_id)
