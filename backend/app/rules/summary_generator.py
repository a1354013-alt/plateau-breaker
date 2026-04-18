from __future__ import annotations

from app.schemas.analytics import (
    FactorContribution,
    PlateauResponse,
    ReasonItem,
    ReasonsResponse,
    SummaryPayload,
)

STATUS_MESSAGES: dict[str, str] = {
    "plateau": "Your weight appears to be in a plateau based on recent trends.",
    "losing": "You're losing weight, keep up the good work.",
    "gaining": "Your weight is trending upward in recent days.",
    "insufficient_data": "Not enough recent data to analyze your trend yet.",
}

REASON_ACTIONS: dict[str, str] = {
    "SleepIssue": "Aim for 7-8 hours of sleep and keep sleep times consistent.",
    "CalorieIssue": "Reduce average calorie intake toward your target and track high-calorie items.",
    "WeekendOvereating": "Plan weekends and keep calories closer to weekday levels.",
    "ExerciseDrop": "Restore activity levels (e.g. 30 minutes/day) to match your previous routine.",
    "DataMissing": "Log daily records consistently to improve analysis confidence.",
}

_FACTOR_NAME: dict[str, str] = {
    "SleepIssue": "low_sleep",
    "CalorieIssue": "calorie_over",
    "WeekendOvereating": "weekend_overeating",
    "ExerciseDrop": "exercise_drop",
    "DataMissing": "missing_data",
}


def _format_reason_line(idx: int, reason: ReasonItem) -> str:
    rank = "Main" if idx == 0 else "Secondary"
    label = reason.label or reason.code or "Unknown"
    return f"{rank} factor: {label}."


def _build_factor_contributions(reasons: list[ReasonItem]) -> list[FactorContribution]:
    if not reasons:
        return []

    total = sum(max(r.severity, 0.0) for r in reasons)
    if total <= 0:
        return []

    factors: list[FactorContribution] = []
    for reason in reasons:
        percent = int(round((reason.severity / total) * 100))
        confidence = max(0.5, min(0.95, round(0.55 + min(reason.severity, 1.0) * 0.4, 2)))
        factors.append(
            FactorContribution(
                factor=_FACTOR_NAME.get(reason.code, reason.code.lower()),
                impact_percent=percent,
                confidence=confidence,
            )
        )

    factors.sort(key=lambda x: x.impact_percent, reverse=True)
    return factors


def generate_summary(plateau_result: PlateauResponse, reason_result: ReasonsResponse) -> SummaryPayload:
    status = plateau_result.status or "insufficient_data"
    reasons: list[ReasonItem] = list(reason_result.reasons or [])

    status_sentence = STATUS_MESSAGES.get(status, STATUS_MESSAGES["insufficient_data"])

    parts: list[str] = []

    if reason_result.status == "insufficient_data":
        parts.append(reason_result.message or "Not enough recent data to analyze reasons yet.")
    elif plateau_result.status == "insufficient_data":
        parts.append(plateau_result.message or "Not enough recent data to detect plateau yet.")
    elif any(r.code == "DataMissing" for r in reasons):
        parts.append("Some recent days are missing and results may be less reliable.")

    parts.append(status_sentence)

    if status != "insufficient_data" and reason_result.status != "insufficient_data":
        for idx, reason in enumerate(reasons[:2]):
            parts.append(_format_reason_line(idx, reason))

    summary_text = " ".join(parts).strip()

    action_lines: list[str] = []
    for reason in reasons[:2]:
        action = REASON_ACTIONS.get(reason.code)
        if action:
            action_lines.append(f"- {action}")

    if action_lines:
        insight_text = "Recommended actions:\n" + "\n".join(action_lines)
    else:
        if status == "losing":
            insight_text = "Recommended actions:\n- Keep doing what works and stay consistent."
        elif status == "insufficient_data":
            insight_text = "Recommended actions:\n- Log at least 5 days of records within the last 7 days to unlock analysis."
        else:
            insight_text = "Recommended actions:\n- Focus on consistency for the next week and review again."

    return SummaryPayload(
        text=summary_text,
        insight=insight_text,
        status=status,
        top_reasons=[r.code for r in reasons],
        factor_contributions=_build_factor_contributions(reasons),
    )
