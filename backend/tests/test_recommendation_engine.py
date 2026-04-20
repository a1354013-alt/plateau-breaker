from __future__ import annotations

from datetime import date, timedelta

from app.models.health_record import HealthRecord
from app.rules import analyze_reasons, detect_plateau, generate_recommendations, generate_summary
from app.schemas.analytics import SummaryResponse


def test_recommendation_engine_returns_sorted_priorities(session):
    anchor = date.today()
    start = anchor - timedelta(days=6)
    for i in range(7):
        d = start + timedelta(days=i)
        session.add(HealthRecord(
            record_date=d,
            weight=75.0,
            sleep_hours=5.0,
            calories=2400,
            protein=60,
            exercise_minutes=10,
        ))
    session.commit()

    from sqlmodel import select
    records = list(session.exec(select(HealthRecord).order_by(HealthRecord.record_date)).all())
    plateau = detect_plateau(records, anchor_date=anchor)
    reasons = analyze_reasons(records, 2000, anchor_date=anchor)
    summary = generate_summary(plateau, reasons)

    response = SummaryResponse(plateau=plateau, reasons=reasons, summary=summary)
    response.recommendations = generate_recommendations(response)

    assert response.recommendations
    assert response.recommendations == sorted(response.recommendations, key=lambda x: x.priority)
