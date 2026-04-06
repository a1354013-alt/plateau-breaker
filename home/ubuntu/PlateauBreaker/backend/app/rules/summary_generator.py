"""
Summary Generator — produces human-readable insight text from plateau status and reasons.
"""

STATUS_MESSAGES = {
    "plateau": "您目前正處於體重高原期。",
    "losing": "進展良好！您正在積極減重。",
    "gaining": "您的體重呈上升趨勢——是時候審視您的習慣了。",
    "insufficient_data": "數據不足，暫無法判斷您的體重趨勢。",
}

REASON_ACTIONS = {
    "SleepIssue": {
        "short": "睡眠不足",
        "action": "目標每晚 7-8 小時優質睡眠。睡眠不足會提高皮質醇，抑制脂肪燃燒。",
    },
    "CalorieIssue": {
        "short": "卡路里攝入過高",
        "action": "審視您的日常飲食，減少份量或高熱量零食，以保持在目標範圍內。",
    },
    "WeekendOvereating": {
        "short": "週末飲食過量",
        "action": "提前規劃週末飲食，避免在休息日暴飲暴食。",
    },
    "ExerciseDrop": {
        "short": "運動量減少",
        "action": "增加每週運動頻率。即使每天步行 30 分鐘也能產生顯著差異。",
    },
    "DataMissing": {
        "short": "追蹤數據不完整",
        "action": "每天記錄您的健康數據，以獲得更準確的分析和更好的洞察。",
    },
}


def generate_summary(plateau_result: dict, reason_result: dict) -> dict:
    status = plateau_result.get("status", "insufficient_data")
    reasons = reason_result.get("reasons", [])

    # Status sentence
    status_sentence = STATUS_MESSAGES.get(status, STATUS_MESSAGES["insufficient_data"])

    # Reason sentences
    reason_sentences = []
    action_sentences = []

    for i, reason in enumerate(reasons):
        code = reason.get("code", "")
        info = REASON_ACTIONS.get(code, {"short": reason.get("label", "unknown"), "action": ""})
        rank_text = "Main cause" if i == 0 else "Secondary cause"
        details = reason.get("details", {})
        detail_text = ""

        if code == "SleepIssue" and details.get("avg_sleep") is not None:
            detail_text = f" (平均 {details['avg_sleep']:.1f} 小時)"
        elif code == "CalorieIssue" and details.get("over_target_percent") is not None:
            detail_text = f" (超出目標 {details['over_target_percent']:.0f}%)"
        elif code == "WeekendOvereating" and details.get("higher_percent") is not None:
            detail_text = f" (比平日平均高 {details['higher_percent']:.0f}%)"
        elif code == "ExerciseDrop" and details.get("drop_percent") is not None:
            detail_text = f" (下降 {details['drop_percent']:.0f}%)"
        elif code == "DataMissing" and details.get("missing_days") is not None:
            detail_text = f" (過去 7 天缺失 {details['missing_days']} 天)"
        
        reason_sentences.append(f"{rank_text}: {info['short']}{detail_text}.")
        if info["action"]:
            action_sentences.append(f"• {info['action']}")

    # Build full summary
    parts = []

    # Prioritize data reliability message if DataMissing is a top reason
    if reason_result.get("status") == "insufficient_data":
        parts.append(reason_result.get("message", "數據不足，無法進行原因分析。"))
    elif plateau_result.get("status") == "insufficient_data":
        parts.append(plateau_result.get("message", "數據不足，無法進行高原期檢測。"))
    elif any(r.get("code") == "DataMissing" for r in reasons):
        parts.append("分析置信度因近期記錄不完整而降低。")

    parts.append(status_sentence)
    if status == "insufficient_data" or reason_result.get("status") == "insufficient_data":
        # If status is insufficient_data, don't add other reasons as they are not reliable
        pass
    else:
        parts.extend(reason_sentences)

    summary_text = " ".join(parts)

    # Build detailed insight
    if action_sentences:
        insight_text = "Recommended actions:\n" + "\n".join(action_sentences)
    else:
        if status == "losing":
            insight_text = "保持您目前的習慣——您的努力正在奏效！"
        elif status == "insufficient_data":
            insight_text = "開始記錄您的每日體重、睡眠和卡路里，以解鎖個性化洞察。"
        else:
            insight_text = "未檢測到特定問題。請繼續監測您的數據以獲取更多洞察。"

    return {
        "summary": summary_text,
        "insight": insight_text,
        "status": status,
        "top_reasons": [r.get("code") for r in reasons],
    }
