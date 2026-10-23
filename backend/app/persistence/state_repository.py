from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from sqlalchemy import JSON, Column, MetaData, String, Table, create_engine, select
from sqlalchemy.engine import Engine


logger = logging.getLogger("intelli_credit.persistence")


class StateRepository:
    """Persists the application snapshot behind a database-neutral interface."""

    def __init__(self, data_dir: Path, legacy_state_file: Path) -> None:
        self._legacy_state_file = legacy_state_file
        self._engine = self._create_engine(data_dir)
        self._metadata = MetaData()
        self._state_table = Table(
            "application_state",
            self._metadata,
            Column("state_key", String(64), primary_key=True),
            Column("payload", JSON, nullable=False),
        )
        self._metadata.create_all(self._engine)

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
        with self._engine.begin() as connection:
            row = connection.execute(
                select(self._state_table.c.payload).where(self._state_table.c.state_key == "global")
            ).scalar_one_or_none()
            if row is not None:
                return dict(row)

        legacy_state = self._load_legacy_state()
        if legacy_state is not None:
            self.save(legacy_state)
            return legacy_state
        return default_state

    def save(self, state: dict[str, Any]) -> None:
        payload = json.loads(json.dumps(state, ensure_ascii=True, default=str))
        with self._engine.begin() as connection:
            updated = connection.execute(
                self._state_table.update()
                .where(self._state_table.c.state_key == "global")
                .values(payload=payload)
            )
            if updated.rowcount == 0:
                connection.execute(self._state_table.insert().values(state_key="global", payload=payload))

    def _load_legacy_state(self) -> dict[str, Any] | None:
        if not self._legacy_state_file.exists():
            return None
        try:
            payload = json.loads(self._legacy_state_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            logger.exception("Legacy application state could not be imported")
            return None
        return payload if isinstance(payload, dict) else None
