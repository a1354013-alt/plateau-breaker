from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import mkdtemp
from typing import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine

backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Ensure app-level smoke tests (importing app.main) never write to the repo tree.
_pytest_tmp_db_dir = Path(mkdtemp(prefix="plateaubreaker_pytest_"))
os.environ.setdefault(
    "PLATEAUBREAKER_DB_PATH",
    str((_pytest_tmp_db_dir / "plateaubreaker_pytest.sqlite3").resolve()),
)


@pytest.fixture(scope="session", autouse=True)
def _dispose_cached_engines() -> Generator[None, None, None]:
    yield
    # Ensure SQLite files are not left locked (Windows) after the test run.
    from app.database import dispose_engine

    dispose_engine()


@pytest.fixture()
def session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
