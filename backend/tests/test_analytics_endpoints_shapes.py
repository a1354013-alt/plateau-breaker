from __future__ import annotations

from datetime import date, timedelta

from app.api.analytics import (
    get_dashboard,
    get_plateau,
    get_reasons,
    get_summary,
    get_trends,
)
from app.models.health_record import HealthRecord
from app.schemas.analytics import (
    DashboardResponse,
    PlateauResponse,
    ReasonsResponse,
    SummaryResponse,
    TrendsResponse,
)
from app.time import get_today


def _seed_records(session, *, anchor: date, days: int = 14) -> None:
    start = anchor - timedelta(days=days - 1)
    for i in range(days):
        d = start + timedelta(days=i)
        session.add(
            HealthRecord(
                record_date=d,
                weight=75.0 + (i * 0.01),
                sleep_hours=7.0,
                calories=2000,
                protein=120,
                exercise_minutes=30,
                exercise_type="Walking",
                steps=8000,
                note=None,
            )
        )
    session.commit()


def test_dashboard_trends_plateau_reasons_summary_shapes(session):
    anchor = get_today()
    _seed_records(session, anchor=anchor, days=14)

    dashboard = get_dashboard(session=session, anchor=anchor)
    assert isinstance(dashboard, DashboardResponse)
    assert dashboard.total_records == 14

    trends = get_trends(days=30, session=session, anchor=anchor)
    assert isinstance(trends, TrendsResponse)
    assert trends.days == 30
    assert trends.data_points >= 0

    plateau = get_plateau(session=session, anchor=anchor)
    assert isinstance(plateau, PlateauResponse)
    assert plateau.status in ("losing", "plateau", "gaining", "insufficient_data")

    reasons = get_reasons(calorie_target=2000, session=session, anchor=anchor)
    assert isinstance(reasons, ReasonsResponse)
    assert reasons.status in ("ok", "insufficient_data")
    assert isinstance(reasons.reasons, list)

    summary = get_summary(calorie_target=2000, session=session, anchor=anchor)
    assert isinstance(summary, SummaryResponse)
    assert summary.summary.text is not None
    assert summary.summary.status in ("losing", "plateau", "gaining", "insufficient_data")
