import pandas as pd
from functools import lru_cache

from utils.constants import (
    IMPORTANCE_PATH, FEATURE_LABELS, FEATURES, NORMAL_RANGES, RISK_THRESHOLDS,
)


# ── Feature importance ─────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def load_importance_map() -> dict:
    """Load feature importance scores and return as {feature: score} dict."""
    try:
        df = pd.read_csv(IMPORTANCE_PATH)
        return dict(zip(df['Feature'], df['Importance']))
    except FileNotFoundError:
        return {}


# ── Abnormality scoring ────────────────────────────────────────────────────────

def abnormality_score(feature: str, value: float) -> float:
    """
    Return a non-negative score representing how far a value deviates from
    its normal range.  Higher → more abnormal in the 'bad' direction.
    """
    if feature not in NORMAL_RANGES:
        return 0.0

    lo, hi, bad_dir = NORMAL_RANGES[feature]
    denom = hi - lo + 1e-9

    if bad_dir == 'high':
        return max(0.0, (value - hi) / denom)
    if bad_dir == 'low':
        return max(0.0, (lo - value) / denom)

    # No directional preference – use distance from midpoint
    mid = (lo + hi) / 2
    return abs(value - mid) / ((hi - lo) / 2 + 1e-9)


# ── Personalised factor ranking ────────────────────────────────────────────────

def get_top_contributing_factors(patient_dict: dict,
                                 top_n: int = 5) -> tuple[list, float]:
    """
    Rank features by importance × (1 + abnormality) for this specific patient.

    Returns:
        top_features  – list of (feature, weighted_score) tuples, descending
        total         – sum of all weighted scores (for percentage calculations)
    """
    importance_map = load_importance_map()
    scores = {
        feature: importance_map.get(feature, 0.0) * (
            1.0 + abnormality_score(feature, patient_dict[feature])
        )
        for feature in FEATURES
    }
    total        = sum(scores.values()) or 1.0
    top_features = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return top_features, total


# ── Clinical risk flags ────────────────────────────────────────────────────────

def get_risk_flags(patient_dict: dict) -> tuple[list, dict]:
    """
    Return a list of (feature, description) pairs for clinically notable values,
    ranked by feature importance.

    Also returns the importance_map for downstream use.
    """
    importance_map = load_importance_map()
    flags: dict[str, str] = {}

    checks = [
        ('ejection_fraction',        lambda v: v < 40,
         lambda v: f"Low ejection fraction ({v}%) — heart pumping below normal range"),
        ('serum_creatinine',         lambda v: v > 2.0,
         lambda v: f"Elevated serum creatinine ({v} mg/dL) — above normal range"),
        ('age',                      lambda v: v > 70,
         lambda v: f"Age {int(v)} — older age associated with higher cardiac risk"),
        ('serum_sodium',             lambda v: v < 130,
         lambda v: f"Low serum sodium ({v} mEq/L) — below normal range"),
        ('diabetes',                 lambda v: v == 1,
         lambda _: "Diabetes present — associated with increased cardiovascular risk"),
        ('high_blood_pressure',      lambda v: v == 1,
         lambda _: "High blood pressure — associated with increased cardiac strain"),
        ('anaemia',                  lambda v: v == 1,
         lambda _: "Anaemia present — associated with reduced oxygen delivery"),
        ('creatinine_phosphokinase', lambda v: v > 1000,
         lambda v: f"Elevated CPK ({v} U/L) — above normal range"),
        ('smoking',                  lambda v: v == 1,
         lambda _: "Smoking present — associated with accelerated arterial damage"),
    ]

    # Platelets: both too low and too high are flagged
    pl = patient_dict.get('platelets', 0)
    if pl < 100_000:
        flags['platelets'] = f"Low platelets ({pl:,.0f}/µL) — below normal range"
    elif pl > 600_000:
        flags['platelets'] = f"High platelets ({pl:,.0f}/µL) — above normal range"

    for feature, condition, message in checks:
        val = patient_dict.get(feature)
        if val is not None and condition(val):
            flags[feature] = message(val)

    if not flags:
        return [], importance_map

    ranked = sorted(flags.items(),
                    key=lambda x: importance_map.get(x[0], 0.0),
                    reverse=True)
    return ranked, importance_map


# ── Prediction explanation bullets ────────────────────────────────────────────

def build_explanation_bullets(patient_dict: dict, prob: float) -> list[str]:
    """
    Return a list of plain-text bullet strings explaining which clinical
    values drove the risk prediction.
    """
    lines: list[str] = []

    ef = patient_dict['ejection_fraction']
    if ef < 40:
        lines.append(
            f"Low ejection fraction ({ef}%) — heart is pumping less than 40% of blood per beat, "
            "indicating reduced cardiac output."
        )
    elif ef < 55:
        lines.append(
            f"Mildly reduced ejection fraction ({ef}%) — below the normal range of 55–70%."
        )

    sc = patient_dict['serum_creatinine']
    if sc > 2.0:
        lines.append(
            f"Elevated serum creatinine ({sc} mg/dL) — above the normal range (0.7–1.2 mg/dL), "
            "suggesting reduced kidney function."
        )
    elif sc > 1.2:
        lines.append(
            f"Borderline serum creatinine ({sc} mg/dL) — slightly above normal, "
            "which may reflect early renal stress."
        )

    sn = patient_dict['serum_sodium']
    if sn < 130:
        lines.append(
            f"Critically low serum sodium ({sn} mEq/L) — severe hyponatremia strongly "
            "associated with poor cardiac outcomes."
        )
    elif sn < 135:
        lines.append(
            f"Low serum sodium ({sn} mEq/L) — below normal (135–145 mEq/L), "
            "which is linked to worse heart failure prognosis."
        )

    age = int(patient_dict['age'])
    if age > 70:
        lines.append(
            f"Advanced age ({age} years) — patients over 70 show higher rates of "
            "adverse outcomes in this dataset."
        )

    comorbidities = {
        'diabetes':          ("Diabetes present — associated with accelerated cardiovascular disease "
                              "and worse heart failure outcomes."),
        'high_blood_pressure':("High blood pressure — increases cardiac workload and is linked to "
                               "higher risk of adverse events."),
        'anaemia':           ("Anaemia present — reduces oxygen-carrying capacity, placing additional "
                              "strain on the heart."),
        'smoking':           ("Smoking — associated with accelerated arterial damage and reduced "
                              "cardiac reserve."),
    }
    for feature, msg in comorbidities.items():
        if patient_dict.get(feature) == 1:
            lines.append(msg)

    cpk = patient_dict['creatinine_phosphokinase']
    if cpk > 1000:
        lines.append(
            f"Elevated CPK ({cpk} U/L) — significantly above normal range, "
            "may indicate myocardial or skeletal muscle stress."
        )

    if not lines:
        lines.append(
            "No individual clinical values are outside normal ranges. "
            "The model's prediction is based on the combined profile of all indicators."
        )

    return lines