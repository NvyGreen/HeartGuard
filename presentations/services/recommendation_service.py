from utils.constants import RISK_THRESHOLDS


# ── Per-tier recommendation copy ───────────────────────────────────────────────

_RECOMMENDATIONS: dict[str, list[str]] = {
    "HIGH": [
        "Consider closer monitoring and follow-up.",
        "Review and optimize heart failure management.",
        "Evaluate need for specialist or advanced care consultation.",
        "Patient may benefit from early intervention strategies.",
    ],
    "MEDIUM": [
        "Schedule follow-up within 7 days.",
        "Monitor serum creatinine and ejection fraction closely.",
        "Consider cardiology referral if symptoms worsen.",
    ],
    "LOW": [
        "Continue routine monitoring.",
        "Reassess if symptoms worsen or new risk factors emerge.",
        "Maintain current management plan.",
    ],
}


def get_recommendations(risk_category: str) -> list[str]:
    """
    Return a list of recommendation strings for the given risk tier.

    Args:
        risk_category: "HIGH" | "MEDIUM" | "LOW"
    """
    return _RECOMMENDATIONS.get(risk_category.upper(), _RECOMMENDATIONS["LOW"])


def get_why_text(prob: float) -> str:
    """Return a one-sentence rationale for the recommendation."""
    direction = "higher" if prob >= RISK_THRESHOLDS["MEDIUM"] else "lower"
    return (
        f"Patients with similar clinical indicators in the historical dataset had a "
        f"{direction} rate of adverse outcomes within the observed follow-up period."
    )