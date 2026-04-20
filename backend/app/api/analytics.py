from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.dependencies.clock import get_anchor_date
from app.rules import analyze_reasons, detect_plateau, generate_recommendations, generate_summary
from app.schemas.analytics import (
    DashboardResponse,
    PlateauResponse,
    ReasonsResponse,
    SummaryResponse,
    TrendsResponse,
    WeeklyReportResponse,
)
from app.services import health_record_service as svc
from app.services.profile_service import get_or_create_profile

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])
report_router = APIRouter(prefix="/api/report", tags=["Report"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    session: Session = Depends(get_session),
    anchor: date = Depends(get_anchor_date),
) -> DashboardResponse:
    all_records = svc.get_all_records_ordered(session)
    last7 = svc.get_records_by_days(session, 7, anchor_date=anchor)

    current_weight = all_records[-1].weight if all_records else None

    avg_weight_7d = None
    avg_sleep_7d = None
    avg_calories_7d = None

    if len(last7) >= 5:
        avg_weight_7d = round(sum(r.weight for r in last7) / len(last7), 2)
        avg_sleep_7d = round(sum(r.sleep_hours for r in last7) / len(last7), 2)
        avg_calories_7d = round(sum(r.calories for r in last7) / len(last7), 1)

    weight_change_7d = None
    if all_records and current_weight is not None:
        weight_by_date = {r.record_date: r.weight for r in all_records}
        target_date = anchor - timedelta(days=7)
        if anchor in weight_by_date and target_date in weight_by_date:
            weight_change_7d = round(weight_by_date[anchor] - weight_by_date[target_date], 2)

    return DashboardResponse.model_validate({
        "current_weight": current_weight,
        "avg_weight_7d": avg_weight_7d,
        "avg_sleep_7d": avg_sleep_7d,
        "avg_calories_7d": avg_calories_7d,
        "weight_change_7d": weight_change_7d,
        "total_records": len(all_records),
        "last_record_date": all_records[-1].record_date.isoformat() if all_records else None,
    })


@router.get("/trends", response_model=TrendsResponse)
def get_trends(
    days: int = Query(default=30, ge=7, le=365),
    session: Session = Depends(get_session),
    anchor: date = Depends(get_anchor_date),
) -> TrendsResponse:
    records = svc.get_records_by_days(session, days, anchor_date=anchor)

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

    return TrendsResponse.model_validate({
        "days": days,
        "data_points": len(trend_data),
        "trends": trend_data,
    })


@router.get("/plateau", response_model=PlateauResponse)
def get_plateau(
    session: Session = Depends(get_session),
    anchor: date = Depends(get_anchor_date),
) -> PlateauResponse:
    all_records = svc.get_all_records_ordered(session)
    return detect_plateau(all_records, anchor_date=anchor)


@router.get("/reasons", response_model=ReasonsResponse)
def get_reasons(
    calorie_target: int = Query(default=2000, ge=1000, le=5000),
    session: Session = Depends(get_session),
    anchor: date = Depends(get_anchor_date),
) -> ReasonsResponse:
    all_records = svc.get_all_records_ordered(session)
    return analyze_reasons(all_records, calorie_target, anchor_date=anchor)


@router.get("/summary", response_model=SummaryResponse)
def get_summary(
    calorie_target: int | None = Query(default=None, ge=1000, le=5000),
    session: Session = Depends(get_session),
    anchor: date = Depends(get_anchor_date),
) -> SummaryResponse:
    all_records = svc.get_all_records_ordered(session)
    profile = get_or_create_profile(session)
    effective_calorie_target = calorie_target or profile.daily_calorie_target

    plateau_result = detect_plateau(all_records, anchor_date=anchor)
    reason_result = analyze_reasons(all_records, effective_calorie_target, anchor_date=anchor)
    summary = generate_summary(plateau_result, reason_result)

    payload = SummaryResponse(plateau=plateau_result, reasons=reason_result, summary=summary)
    payload.recommendations = generate_recommendations(payload)
    return payload


@report_router.get("/weekly", response_model=WeeklyReportResponse)
def get_weekly_report(
    session: Session = Depends(get_session),
    anchor: date = Depends(get_anchor_date),
) -> WeeklyReportResponse:
    summary_payload = get_summary(session=session, anchor=anchor)
    metrics = get_dashboard(session=session, anchor=anchor)

    return WeeklyReportResponse(
        summary=summary_payload.summary,
        metrics=metrics,
        plateau_status=summary_payload.plateau.status,
        reasons=summary_payload.reasons.reasons,
        recommendations=summary_payload.recommendations,
    )
