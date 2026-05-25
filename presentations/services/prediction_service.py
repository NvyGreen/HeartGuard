import pickle
import pandas as pd
from functools import lru_cache

from utils.constants import PIPELINE_PATH, FEATURES, RISK_THRESHOLDS, RISK_COLORS, RISK_LABELS


# ── Pipeline loading ───────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def load_pipeline():
    """Load and cache the trained sklearn pipeline from disk."""
    with open(PIPELINE_PATH, 'rb') as f:
        return pickle.load(f)


# ── Scoring ────────────────────────────────────────────────────────────────────

def predict_proba(patient_dict: dict) -> float:
    """Return the probability of adverse outcome (DEATH_EVENT = 1) for one patient."""
    pipeline = load_pipeline()
    df = pd.DataFrame([patient_dict])[FEATURES]
    return float(pipeline.predict_proba(df)[0][1])


# ── Risk categorisation ────────────────────────────────────────────────────────

def get_risk_category(prob: float) -> dict:
    """
    Map a probability to a risk tier.

    Returns a dict with keys:
        category  – "HIGH" | "MEDIUM" | "LOW"
        label     – human-readable label
        color     – hex colour string
    """
    if prob >= RISK_THRESHOLDS['HIGH']:
        tier = 'HIGH'
    elif prob >= RISK_THRESHOLDS['MEDIUM']:
        tier = 'MEDIUM'
    else:
        tier = 'LOW'

    return {
        'category': tier,
        'label':    RISK_LABELS[tier],
        'color':    RISK_COLORS[tier],
    }


def score_patient(patient_dict: dict) -> tuple[float, dict]:
    """
    Convenience wrapper: returns (probability, risk_category_dict).
    """
    prob = predict_proba(patient_dict)
    return prob, get_risk_category(prob)