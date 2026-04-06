"""
Plateau Detection Rules:
  Rule A: Average weight of last 7 days vs previous 7 days — change < 0.2 kg → plateau
  Rule B: Weight fluctuation within last 7 days stays within ±0.3 kg → plateau

Returns: "losing" | "plateau" | "gaining"
"""
from datetime import date, timedelta
from typing import Literal

from app.models.health_record import HealthRecord


PlateauStatus = Literal["losing", "plateau", "gaining", "insufficient_data"]


def detect_plateau(records: list[HealthRecord]) -> dict:
    """
    Analyse records and return plateau status with detailed metrics.
    Records should be sorted by record_date ascending.
    """
    if not records:
        return {
            "status": "insufficient_data",
            "message": "No data available for plateau detection.",
            "rule_a": None,
            "rule_b": None,
            "last7_avg": None,
            "prev7_avg": None,
            "last7_fluctuation": None,
            "last7_min": None,
            "last7_max": None,
        }

    latest_date = records[-1].record_date
    last7_start = latest_date - timedelta(days=6)
    prev7_start = latest_date - timedelta(days=13)
    prev7_end = latest_date - timedelta(days=7)

    last7 = [r for r in records if r.record_date >= last7_start and r.record_date <= latest_date]
    prev7 = [r for r in records if r.record_date >= prev7_start and r.record_date <= prev7_end]

    data_completeness_score = len(last7) / 7.0
    if len(last7) < 5:
        return {
            "status": "insufficient_data",
            "message": "Need at least 5 days of recent data for plateau detection.",
            "rule_a": None,
            "rule_b": None,
            "last7_avg": None,
            "prev7_avg": None,
            "last7_fluctuation": None,
            "last7_min": None,
            "last7_max": None,
            "data_completeness": data_completeness_score,
        }


    last7_weights = [r.weight for r in last7]
    last7_avg = sum(last7_weights) / len(last7_weights)
    last7_min = min(last7_weights)
    last7_max = max(last7_weights)
    last7_fluctuation = last7_max - last7_min

    # Rule B: fluctuation within ±0.3 kg
    rule_b_plateau = last7_fluctuation <= 0.6  # max - min <= 0.6 means within ±0.3

    # Rule A: compare with previous 7 days if available
    rule_a_plateau = None
    prev7_avg = None
    avg_change = None

    if len(prev7) >= 7:
        prev7_weights = [r.weight for r in prev7]
        prev7_avg = sum(prev7_weights) / len(prev7_weights)
        avg_change = last7_avg - prev7_avg
        rule_a_plateau = abs(avg_change) < 0.2
    else:
        # Not enough data for Rule A — rely on Rule B only
        rule_a_plateau = None

    # Determine final status
    if rule_a_plateau is not None and len(prev7) >= 5: # Ensure enough data for Rule A comparison
        # Both rules available
        if rule_a_plateau and rule_b_plateau:
            status: PlateauStatus = "plateau"
        elif avg_change is not None and avg_change <= -0.2:
            status = "losing"
        elif avg_change is not None and avg_change >= 0.2:
            status = "gaining"
        else:
            # Rule A borderline — use Rule B as tiebreaker
            status = "plateau" if rule_b_plateau else "losing"
    else:
        # Only Rule B available or not enough prev7 data for Rule A
        if rule_b_plateau:
            status = "plateau"
        else:
            # Determine direction from first vs last of last 7 days
            direction = last7_weights[-1] - last7_weights[0]
            status = "losing" if direction < 0 else "gaining"

    # Add data completeness to the result
    result = {
        "status": status,
        "rule_a": rule_a_plateau,
        "rule_b": rule_b_plateau,
        "last7_avg": round(last7_avg, 2),
        "prev7_avg": round(prev7_avg, 2) if prev7_avg is not None else None,
        "avg_change": round(avg_change, 2) if avg_change is not None else None,
        "last7_fluctuation": round(last7_fluctuation, 2),
        "last7_min": round(last7_min, 2),
        "last7_max": round(last7_max, 2),
        "data_completeness": data_completeness_score,
    }

    if data_completeness_score < 1.0 and status != "insufficient_data":
        result["message"] = f"Analysis based on {len(last7)}/{7} days of data. Confidence reduced due to missing records."

    return result


