from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.time import get_today


def test_get_today_respects_app_timezone_env():
    now = datetime(2026, 1, 1, 0, 30, tzinfo=UTC)

    taipei = get_today(now=now, env={"APP_TIMEZONE": "Asia/Taipei"})
    la = get_today(now=now, env={"APP_TIMEZONE": "America/Los_Angeles"})

    assert taipei.isoformat() == "2026-01-01"
    assert la.isoformat() == "2025-12-31"


def test_get_today_rejects_invalid_timezone():
    now = datetime(2026, 1, 1, 0, 30, tzinfo=UTC)
    with pytest.raises(ValueError):
        get_today(now=now, env={"APP_TIMEZONE": "Not/A_Timezone"})

