from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.database import dispose_engine, resolve_database_url
from app.main import app
from app.migrations import upgrade_to_head


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    db_path = (tmp_path / "integration.sqlite3").resolve()
    monkeypatch.setenv("PLATEAUBREAKER_DB_PATH", str(db_path))

    # Ensure the test DB schema is always explicitly created by Alembic and does
    # not rely on app startup side effects.
    dispose_engine()
    upgrade_to_head(sqlalchemy_url=resolve_database_url())

    with TestClient(app) as test_client:
        yield test_client

    dispose_engine()

