"""
Reason Analysis Rules (evaluated on last 7 days):
  1. SleepIssue       — avg sleep < 6h
  2. CalorieIssue     — avg calories > target (default 2000)
  3. WeekendOvereating — weekend avg calories > weekday avg by 20%
  4. ExerciseDrop     — recent exercise < previous 7 days * 70%
  5. DataMissing      — missing > 2 days in last 7 days

Returns top-2 ranked reasons.
"""
from datetime import date, timedelta

from typing import Optional
from app.models.health_record import HealthRecord





# Severity weights for each reason type (normalized to 0-1 scale)
SEVERITY_WEIGHTS = {
    "SleepIssue": 1.0,
    "CalorieIssue": 1.0,
    "WeekendOvereating": 0.8,
    "ExerciseDrop": 0.8,
    "DataMissing": 1.2, # Prioritize data missing as it affects analysis confidence
}
SLEEP_THRESHOLD = 6.0
WEEKEND_OVEREATING_RATIO = 1.20
EXERCISE_DROP_RATIO = 0.70
MAX_MISSING_DAYS = 2


def analyze_reasons(records: list[HealthRecord], calorie_target: int) -> dict:
    """
    Analyse records and return ranked reasons for plateau.
    Records should be sorted by record_date ascending.
    """
    if not records:
        return {"status": "insufficient_data", "message": "No data available for reason analysis.", "reasons": [], "all_reasons": [], "data_points": 0, "missing_days": 7}

    latest_date = records[-1].record_date
    last7_start = latest_date - timedelta(days=6)
    prev7_start = latest_date - timedelta(days=13)
    prev7_end = latest_date - timedelta(days=7)

    # Partition records
    last7 = [r for r in records if r.record_date >= last7_start and r.record_date <= latest_date]
    prev7 = [r for r in records if r.record_date >= prev7_start and r.record_date <= prev7_end]

    if len(last7) < 5:
        return {"status": "insufficient_data", "message": "Need at least 5 days of recent data for reason analysis.", "reasons": [], "all_reasons": [], "data_points": len(last7), "missing_days": 7 - len(last7)}

    reasons = []

    # ── Rule 1: Sleep Issue ──────────────────────────────────────────────────
    if last7:
        avg_sleep = sum(r.sleep_hours for r in last7) / len(last7)
        if avg_sleep < SLEEP_THRESHOLD:
            reasons.append({
                "code": "SleepIssue",
                "label": "Insufficient Sleep",
                "description": f"Average sleep last 7 days: {avg_sleep:.1f}h (threshold: {SLEEP_THRESHOLD}h)",
                "severity": round(((SLEEP_THRESHOLD - avg_sleep) / SLEEP_THRESHOLD) * SEVERITY_WEIGHTS["SleepIssue"], 3),
                "value": round(avg_sleep, 2),
                "threshold": SLEEP_THRESHOLD,
                "details": {"avg_sleep": round(avg_sleep, 1), "threshold": SLEEP_THRESHOLD}
            })

    # ── Rule 2: Calorie Issue ────────────────────────────────────────────────
    if last7:
        avg_calories = sum(r.calories for r in last7) / len(last7)
        if avg_calories > calorie_target:
            excess_ratio = (avg_calories - calorie_target) / calorie_target
            reasons.append({
                "code": "CalorieIssue",
                "label": "High Calorie Intake",
                "description": f"Average calories last 7 days: {avg_calories:.0f} kcal (target: {calorie_target} kcal)",
                "severity": round(excess_ratio * SEVERITY_WEIGHTS["CalorieIssue"], 3),
                "value": round(avg_calories, 1),
                "threshold": calorie_target,
                "details": {"avg_calories": round(avg_calories, 0), "target": calorie_target, "over_target_percent": round(excess_ratio * 100, 0)}
            })

    # ── Rule 3: Weekend Overeating ───────────────────────────────────────────
    if last7:
        weekend_records = [r for r in last7 if r.record_date.weekday() >= 5]
        weekday_records = [r for r in last7 if r.record_date.weekday() < 5]
        if weekend_records and weekday_records:
            weekend_avg = sum(r.calories for r in weekend_records) / len(weekend_records)
            weekday_avg = sum(r.calories for r in weekday_records) / len(weekday_records)
            if weekday_avg > 0 and weekend_avg > weekday_avg * WEEKEND_OVEREATING_RATIO:
                ratio = weekend_avg / weekday_avg
                reasons.append({
                    "code": "WeekendOvereating",
                    "label": "Weekend Overeating",
                    "description": f"Weekend avg: {weekend_avg:.0f} kcal, {((ratio - 1) * 100):.0f}% higher than weekday avg: {weekday_avg:.0f} kcal",
                    "severity": round((ratio - 1.0) * SEVERITY_WEIGHTS["WeekendOvereating"], 3),
                    "value": round(weekend_avg, 1),
                    "threshold": round(weekday_avg * WEEKEND_OVEREATING_RATIO, 1),
                    "details": {"weekend_avg": round(weekend_avg, 0), "weekday_avg": round(weekday_avg, 0), "higher_percent": round((ratio - 1) * 100, 0)}
                })

    # ── Rule 4: Exercise Drop ────────────────────────────────────────────────
    if last7 and prev7 and len(prev7) >= 5: # Ensure enough previous data for comparison
        last7_exercise = sum(r.exercise_minutes for r in last7) / len(last7)
        prev7_exercise = sum(r.exercise_minutes for r in prev7) / len(prev7)
        if prev7_exercise > 0 and last7_exercise < prev7_exercise * EXERCISE_DROP_RATIO:
            drop_ratio = 1.0 - (last7_exercise / prev7_exercise)
            reasons.append({
                "code": "ExerciseDrop",
                "label": "Exercise Reduction",
                "description": f"Recent exercise: {last7_exercise:.0f} min/day vs Previous: {prev7_exercise:.0f} min/day",
                "severity": round(drop_ratio * SEVERITY_WEIGHTS["ExerciseDrop"], 3),
                "value": round(last7_exercise, 1),
                "threshold": round(prev7_exercise * EXERCISE_DROP_RATIO, 1),
                "details": {"last7_exercise": round(last7_exercise, 0), "prev7_exercise": round(prev7_exercise, 0), "drop_percent": round(drop_ratio * 100, 0)}
            })

    # ── Rule 5: Data Missing ─────────────────────────────────────────────────
    expected_dates = {last7_start + timedelta(days=i) for i in range(7)}
    actual_dates = {r.record_date for r in last7}
    missing_count = len(expected_dates - actual_dates)
    if missing_count > MAX_MISSING_DAYS:
        reasons.append({
            "code": "DataMissing",
            "label": "Incomplete Data",
            "description": f"Missing {missing_count} days of records in the last 7 days",
            "severity": round((missing_count / 7) * SEVERITY_WEIGHTS["DataMissing"], 3),
            "value": missing_count,
            "threshold": MAX_MISSING_DAYS,
            "details": {"missing_days": missing_count}
        })

    # Sort by severity descending and return top 2
    reasons.sort(key=lambda x: x["severity"], reverse=True)
    top2 = reasons[:2]

    result = {
        "status": "ok",
        "reasons": top2,
        "all_reasons": reasons,
        "data_points": len(last7),
        "missing_days": missing_count,
    }

    if missing_count > 0:
        result["message"] = f"Analysis based on {len(last7)}/{7} days of data. Confidence reduced due to {missing_count} missing records."

    return result
