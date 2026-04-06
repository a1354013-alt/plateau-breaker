from datetime import date, timedelta
from typing import Literal, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.database import get_session
from app.services import health_record_service as svc
from app.rules import detect_plateau, analyze_reasons, generate_summary

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard(session: Session = Depends(get_session)):
    """Return KPI metrics for the dashboard."""
    all_records = svc.get_all_records_ordered(session)
    last7 = svc.get_records_by_days(session, 7)

    current_weight = None
    if all_records:
        current_weight = all_records[-1].weight

    avg_weight_7d = None
    avg_sleep_7d = None
    avg_calories_7d = None

    if last7:
        avg_weight_7d = round(sum(r.weight for r in last7) / len(last7), 2)
        avg_sleep_7d = round(sum(r.sleep_hours for r in last7) / len(last7), 2)
        avg_calories_7d = round(sum(r.calories for r in last7) / len(last7), 1)

    # Weight change vs 7 days ago
    weight_change_7d = None
    if len(all_records) >= 2:
        latest_date = all_records[-1].record_date
        seven_days_ago = latest_date - timedelta(days=7)
        older = [r for r in all_records if r.record_date <= seven_days_ago]
        if older and current_weight is not None:
            weight_change_7d = round(current_weight - older[-1].weight, 2)

    return {
        "current_weight": current_weight,
        "avg_weight_7d": avg_weight_7d,
        "avg_sleep_7d": avg_sleep_7d,
        "avg_calories_7d": avg_calories_7d,
        "weight_change_7d": weight_change_7d,
        "total_records": len(all_records),
        "last_record_date": all_records[-1].record_date.isoformat() if all_records else None,
    }


@router.get("/trends")
def get_trends(
    days: int = Query(default=30, ge=7, le=365),
    session: Session = Depends(get_session),
):
    """Return time-series data for trend charts."""
    records = svc.get_records_by_days(session, days)

    trend_data = [
        {
            "date": r.record_date.isoformat(),
            "weight": r.weight,
            "sleep_hours": r.sleep_hours,
            "calories": r.calories,
            "exercise_minutes": r.exercise_minutes,
            "steps": r.steps,
        }
        for r in records
    ]

    return {
        "days": days,
        "data_points": len(trend_data),
        "trends": trend_data,
    }


@router.get("/plateau")
def get_plateau(session: Session = Depends(get_session)):
    """Detect current plateau status."""
    all_records = svc.get_all_records_ordered(session)
    result = detect_plateau(all_records)
    return result


@router.get("/reasons")
def get_reasons(
    calorie_target: int = Query(default=2000, ge=1000, le=5000),
    session: Session = Depends(get_session),
):
    """Analyse reasons for weight plateau."""
    all_records = svc.get_all_records_ordered(session)
    result = analyze_reasons(all_records, calorie_target)
    return result


@router.get("/summary")
def get_summary(
    calorie_target: int = Query(default=2000, ge=1000, le=5000),
    session: Session = Depends(get_session),
):
    """Generate human-readable summary combining plateau status and reasons."""
    all_records = svc.get_all_records_ordered(session)
    plateau_result = detect_plateau(all_records)
    reason_result = analyze_reasons(all_records, calorie_target)
    summary = generate_summary(plateau_result, reason_result)

    return {
        "plateau": plateau_result,
        "reasons": reason_result,
        "summary": summary,
    }
