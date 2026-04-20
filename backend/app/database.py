from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path
from typing import Optional

from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine


def _resolve_db_path() -> Path:
    """Resolve the SQLite file path (independent of process working directory).

    Env override:
    - PLATEAUBREAKER_DB_PATH: absolute path OR path relative to the `backend/` directory.
      For convenience, a relative path starting with `backend/` is treated as repo-root relative.

    Default:
    - backend/data/plateaubreaker.sqlite3
    """

    backend_dir = Path(__file__).resolve().parents[1]
    repo_root = backend_dir.parent
    configured = os.getenv("PLATEAUBREAKER_DB_PATH")

    if configured and configured.strip():
        raw = configured.strip()
        p = Path(raw)
        if p.is_absolute():
            db_path = p
        else:
            parts = Path(raw).parts
            if parts and parts[0].lower() == "backend":
                db_path = repo_root / p
            else:
                db_path = backend_dir / p
    else:
        db_path = backend_dir / "data" / "plateaubreaker.sqlite3"

    return db_path.resolve()


def ensure_db_dir_exists() -> None:
    db_path = _resolve_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)


def _resolve_db_url() -> str:
    db_path = _resolve_db_path()
    return f"sqlite:///{db_path.as_posix()}"


def resolve_database_url() -> str:
    """Compute the SQLAlchemy URL based on current env/config."""

    return _resolve_db_url()

# Back-compat constants: these reflect env at import time.
DATABASE_URL = resolve_database_url()


_engines_by_url: dict[str, Engine] = {}


def get_engine(*, sqlalchemy_url: Optional[str] = None) -> Engine:
    """Return a (cached) Engine for the given URL (or current env URL)."""

    url = sqlalchemy_url or resolve_database_url()
    engine = _engines_by_url.get(url)
    if engine is None:
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False,
        )
        _engines_by_url[url] = engine
    return engine


def dispose_engine(*, sqlalchemy_url: Optional[str] = None) -> None:
    """Dispose one engine (by URL) or all cached engines."""

    if sqlalchemy_url is None:
        urls = list(_engines_by_url.keys())
        for url in urls:
            engine = _engines_by_url.pop(url, None)
            if engine is not None:
                engine.dispose()
        return

    engine = _engines_by_url.pop(sqlalchemy_url, None)
    if engine is not None:
        engine.dispose()


# Back-compat name: some scripts import this directly.
engine = get_engine(sqlalchemy_url=DATABASE_URL)


def create_db_and_tables() -> None:
    ensure_db_dir_exists()
    # Bootstrap only when the database is empty. We intentionally apply Alembic
    # migrations instead of `SQLModel.metadata.create_all` so DB-level contracts
    # (CHECK constraints, column lengths, etc.) are enforced even if someone
    # writes directly to the DB without going through the API.
    url = resolve_database_url()
    inspector = inspect(get_engine(sqlalchemy_url=url))
    if inspector.get_table_names():
        return
    from app.migrations import upgrade_to_head

    upgrade_to_head(sqlalchemy_url=url)


def get_session() -> Generator[Session, None, None]:
    ensure_db_dir_exists()
    with Session(get_engine()) as session:
        yield session
