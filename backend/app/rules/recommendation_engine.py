from __future__ import annotations

from app.schemas.analytics import ActionRecommendation, SummaryResponse

_REASON_ACTIONS: dict[str, tuple[int, str, float]] = {
    "CalorieIssue": (1, "Reduce daily calories by 200 kcal", 0.82),
    "SleepIssue": (2, "Improve sleep consistency to at least 7 hours", 0.78),
    "ExerciseDrop": (3, "Increase daily exercise by 20-30 minutes", 0.76),
    "WeekendOvereating": (4, "Use a weekend meal plan to reduce overeating", 0.74),
    "DataMissing": (1, "Log missing days to improve analysis confidence", 0.88),
}


def generate_recommendations(summary: SummaryResponse) -> list[ActionRecommendation]:
    recommendations: list[ActionRecommendation] = []

    for reason in summary.reasons.reasons:
        mapped = _REASON_ACTIONS.get(reason.code)
        if mapped is None:
            continue
        priority, message, base_confidence = mapped
        confidence = max(0.5, min(0.95, round(base_confidence * (0.7 + (reason.severity * 0.3)), 2)))
        recommendations.append(
            ActionRecommendation(
                priority=priority,
                message=message,
                confidence=confidence,
            )
        )

    if not recommendations:
        recommendations.append(
            ActionRecommendation(
                priority=1,
                message="Maintain current routine and keep tracking daily records",
                confidence=0.65,
            )
        )

    recommendations.sort(key=lambda x: x.priority)
    return recommendations
