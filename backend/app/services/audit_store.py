from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APP_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = APP_ROOT / "data"
AUDIT_DB_PATH = DATA_DIR / "audit_log.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(AUDIT_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_audit_store() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                entity_id TEXT,
                company_name TEXT,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute("CREATE INDEX IF NOT EXISTS idx_audit_events_entity ON audit_events(entity_id)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_audit_events_type ON audit_events(event_type)")


def record_audit_event(event_type: str, payload: dict[str, Any], entity_id: str | None = None, company_name: str | None = None) -> None:
    initialize_audit_store()
    created_at = datetime.now(timezone.utc).isoformat()
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO audit_events (event_type, entity_id, company_name, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                event_type,
                entity_id,
                company_name,
                json.dumps(payload, ensure_ascii=True),
                created_at,
            ),
        )


def list_audit_events(entity_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    initialize_audit_store()
    query = "SELECT event_type, entity_id, company_name, payload_json, created_at FROM audit_events"
    params: list[Any] = []
    if entity_id:
        query += " WHERE entity_id = ?"
        params.append(entity_id)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    with _connect() as connection:
        rows = connection.execute(query, params).fetchall()

    events: list[dict[str, Any]] = []
    for row in rows:
        payload = json.loads(row["payload_json"])
        events.append(
            {
                "event_type": row["event_type"],
                "entity_id": row["entity_id"],
                "company_name": row["company_name"],
                "payload": payload,
                "created_at": row["created_at"],
            }
        )
    return events


def clear_audit_events() -> None:
    initialize_audit_store()
    with _connect() as connection:
        connection.execute("DELETE FROM audit_events")