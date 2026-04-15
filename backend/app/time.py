from __future__ import annotations

import os
from datetime import UTC, date, datetime, timezone
from zoneinfo import ZoneInfo

DEFAULT_APP_TIMEZONE = "Asia/Taipei"


def get_app_timezone_name(env: dict[str, str] | None = None) -> str:
    environ = env if env is not None else os.environ
    name = (environ.get("APP_TIMEZONE") or DEFAULT_APP_TIMEZONE).strip()
    return name or DEFAULT_APP_TIMEZONE


def get_app_timezone(env: dict[str, str] | None = None) -> ZoneInfo:
    name = get_app_timezone_name(env)
    try:
        return ZoneInfo(name)
    except Exception as exc:  # pragma: no cover (ZoneInfo error types vary by platform)
        raise ValueError(f"Invalid APP_TIMEZONE: {name}") from exc


def utcnow() -> datetime:
    """Return a timezone-aware UTC datetime."""

    return datetime.now(timezone.utc)


def ensure_utc_aware(value: datetime) -> datetime:
    """Normalize datetimes to timezone-aware UTC.

    - Naive datetimes are treated as UTC (legacy DB rows).
    - Aware datetimes are converted to UTC.
    """

    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def format_datetime_utc_z(value: datetime) -> str:
    dt = ensure_utc_aware(value)
    # Use ISO 8601 with `Z` suffix for UTC to make the contract unambiguous.
    return dt.isoformat().replace("+00:00", "Z")


def get_today(*, now: datetime | None = None, env: dict[str, str] | None = None) -> date:
    """Return the user's calendar 'today' based on APP_TIMEZONE (default Asia/Taipei).

    This avoids semantic drift when the server runs on UTC (or any other timezone).
    """

    tz = get_app_timezone(env)
    current = now if now is not None else utcnow()
    return current.astimezone(tz).date()

