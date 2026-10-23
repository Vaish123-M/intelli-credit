from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Float,
    MetaData,
    String,
    Table,
    create_engine,
    delete,
    inspect,
    select,
)
from sqlalchemy.engine import Engine


logger = logging.getLogger("intelli_credit.persistence")


class StateRepository:
    """Persists application state in relational tables with JSON detail columns."""

    _METADATA_KEYS = (
        "uploaded_files",
        "extracted_data",
        "analysis",
        "research",
        "decision",
        "deals",
        "runs",
        "current_entity_id",
    )
    _STATE_SHAPE_KEY = "_state_shape"

    def __init__(self, data_dir: Path, legacy_state_file: Path) -> None:
        self._legacy_state_file = legacy_state_file
        self._engine = self._create_engine(data_dir)
        self._metadata = MetaData()
        self._users_table = Table(
            "users",
            self._metadata,
            Column("user_id", String(128), primary_key=True),
            Column("email", String(320), nullable=False),
            Column("username", String(128), nullable=False),
            Column("full_name", String(255)),
            Column("role", String(64), nullable=False),
            Column("is_active", Boolean, nullable=False),
            Column("created_at", String(64), nullable=False),
            Column("hashed_password", String(255), nullable=False),
        )
        self._entities_table = Table(
            "entities",
            self._metadata,
            Column("entity_id", String(128), primary_key=True),
            Column("company_name", String(255), nullable=False),
            Column("cin", String(64), nullable=False),
            Column("pan", String(64), nullable=False),
            Column("sector", String(255), nullable=False),
            Column("annual_turnover", Float, nullable=False),
            Column("loan_type", String(128), nullable=False),
            Column("loan_amount", Float, nullable=False),
            Column("loan_tenure", String(128), nullable=False),
            Column("interest_rate", Float, nullable=False),
            Column("created_at", String(64), nullable=False),
            Column("details", JSON, nullable=False),
        )
        self._metadata_table = Table(
            "application_metadata",
            self._metadata,
            Column("metadata_key", String(128), primary_key=True),
            Column("payload", JSON, nullable=False),
        )
        self._legacy_snapshot_table = Table(
            "application_state",
            self._metadata,
            Column("state_key", String(64), primary_key=True),
            Column("payload", JSON, nullable=False),
        )
        self._metadata.create_all(
            self._engine,
            tables=[self._users_table, self._entities_table, self._metadata_table],
        )

    @staticmethod
    def _create_engine(data_dir: Path) -> Engine:
        database_url = os.getenv("DATABASE_URL", "").strip()
        if not database_url:
            database_url = f"sqlite:///{(data_dir / 'app_state.db').as_posix()}"
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        return create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)

    def load(self, default_state: dict[str, Any]) -> dict[str, Any]:
        snapshot: dict[str, Any] | None = None
        with self._engine.begin() as connection:
            state = self._load_relational_state(connection)
            if state is not None:
                return state
            snapshot = self._load_legacy_snapshot(connection)
        if snapshot is not None:
            self.save(snapshot)
            return snapshot

        legacy_state = self._load_legacy_state()
        if legacy_state is not None:
            self.save(legacy_state)
            return legacy_state
        return default_state

    def _load_legacy_snapshot(self, connection) -> dict[str, Any] | None:
        if not inspect(self._engine).has_table("application_state"):
            return None
        payload = connection.execute(
            select(self._legacy_snapshot_table.c.payload).where(
                self._legacy_snapshot_table.c.state_key == "global"
            )
        ).scalar_one_or_none()
        return dict(payload) if isinstance(payload, dict) else None

    def save(self, state: dict[str, Any]) -> None:
        payload = self._json_safe(state)
        with self._engine.begin() as connection:
            connection.execute(delete(self._users_table))
            connection.execute(delete(self._entities_table))
            connection.execute(delete(self._metadata_table))

            users = payload.get("users") or {}
            user_rows = [self._user_row(user_id, user) for user_id, user in users.items()]
            if user_rows:
                connection.execute(self._users_table.insert(), user_rows)

            entities = payload.get("entities") or {}
            entity_rows = [
                self._entity_row(entity_id, entity) for entity_id, entity in entities.items()
            ]
            if entity_rows:
                connection.execute(self._entities_table.insert(), entity_rows)

            metadata_rows = [
                {"metadata_key": key, "payload": payload.get(key)}
                for key in self._METADATA_KEYS
                if key in payload
            ]
            metadata_rows.append(
                {
                    "metadata_key": self._STATE_SHAPE_KEY,
                    "payload": list(payload),
                }
            )
            if metadata_rows:
                connection.execute(self._metadata_table.insert(), metadata_rows)

    def _load_relational_state(self, connection) -> dict[str, Any] | None:
        users = connection.execute(select(self._users_table)).mappings().all()
        entities = connection.execute(select(self._entities_table)).mappings().all()
        metadata = connection.execute(select(self._metadata_table)).mappings().all()
        if not users and not entities and not metadata:
            return None

        state: dict[str, Any] = {"entities": {row["entity_id"]: self._entity_payload(row) for row in entities}}
        state_shape = next(
            (row["payload"] for row in metadata if row["metadata_key"] == self._STATE_SHAPE_KEY),
            [],
        )
        if users or "users" in state_shape:
            state["users"] = {row["user_id"]: self._user_payload(row) for row in users}
        state.update(
            {
                row["metadata_key"]: row["payload"]
                for row in metadata
                if row["metadata_key"] != self._STATE_SHAPE_KEY
            }
        )
        return state

    @staticmethod
    def _user_row(user_id: str, user: dict[str, Any]) -> dict[str, Any]:
        return {
            "user_id": user_id,
            "email": user.get("email", ""),
            "username": user.get("username", ""),
            "full_name": user.get("full_name"),
            "role": user.get("role", "analyst"),
            "is_active": bool(user.get("is_active", True)),
            "created_at": user.get("created_at", ""),
            "hashed_password": user.get("hashed_password", ""),
        }

    @staticmethod
    def _user_payload(row) -> dict[str, Any]:
        return {
            "id": row["user_id"],
            "email": row["email"],
            "username": row["username"],
            "full_name": row["full_name"],
            "role": row["role"],
            "is_active": row["is_active"],
            "created_at": row["created_at"],
            "hashed_password": row["hashed_password"],
        }

    @staticmethod
    def _entity_row(entity_id: str, entity: dict[str, Any]) -> dict[str, Any]:
        return {
            "entity_id": entity_id,
            "company_name": entity.get("company_name", ""),
            "cin": entity.get("cin", ""),
            "pan": entity.get("pan", ""),
            "sector": entity.get("sector", ""),
            "annual_turnover": float(entity.get("annual_turnover", 0)),
            "loan_type": entity.get("loan_type", ""),
            "loan_amount": float(entity.get("loan_amount", 0)),
            "loan_tenure": entity.get("loan_tenure", ""),
            "interest_rate": float(entity.get("interest_rate", 0)),
            "created_at": entity.get("created_at", ""),
            "details": entity,
        }

    @staticmethod
    def _entity_payload(row) -> dict[str, Any]:
        return dict(row["details"])

    @staticmethod
    def _json_safe(value: Any) -> Any:
        return json.loads(json.dumps(value, ensure_ascii=True, default=str))

    def _load_legacy_state(self) -> dict[str, Any] | None:
        if not self._legacy_state_file.exists():
            return None
        try:
            payload = json.loads(self._legacy_state_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            logger.exception("Legacy application state could not be imported")
            return None
        return payload if isinstance(payload, dict) else None
