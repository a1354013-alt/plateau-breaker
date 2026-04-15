from __future__ import annotations

from datetime import date

from app.time import get_today


def get_anchor_date() -> date:
    """FastAPI dependency: single source of truth for 'today' semantics."""

    return get_today()

