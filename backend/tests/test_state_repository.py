from __future__ import annotations

import json

from sqlalchemy import inspect

from app.persistence import StateRepository


def test_state_repository_round_trips_state(tmp_path) -> None:
    repository = StateRepository(tmp_path, tmp_path / "legacy.json")
    state = {"entities": {"ent_1": {"company_name": "Acme"}}, "runs": []}

    repository.save(state)

    assert repository.load({}) == state
    tables = inspect(repository._engine).get_table_names()
    assert {"users", "entities", "application_metadata"} <= set(tables)
    assert "application_state" not in tables


def test_state_repository_imports_legacy_json_once(tmp_path) -> None:
    legacy_path = tmp_path / "app_state.json"
    legacy_state = {"users": {}, "entities": {}, "runs": [{"run_id": "run_1"}]}
    legacy_path.write_text(json.dumps(legacy_state), encoding="utf-8")
    repository = StateRepository(tmp_path, legacy_path)

    assert repository.load({}) == legacy_state
    legacy_path.unlink()
    assert repository.load({}) == legacy_state


def test_state_repository_migrates_snapshot_table(tmp_path) -> None:
    repository = StateRepository(tmp_path, tmp_path / "legacy.json")
    snapshot = {"users": {}, "entities": {"ent_1": {"company_name": "Acme"}}}
    repository._legacy_snapshot_table.create(repository._engine)
    with repository._engine.begin() as connection:
        connection.execute(
            repository._legacy_snapshot_table.insert().values(
                state_key="global",
                payload=snapshot,
            )
        )

    assert repository.load({}) == snapshot
    assert repository.load({}) == snapshot
