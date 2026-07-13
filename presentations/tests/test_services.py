"""
Unit tests for HeartGuard's pure-logic services.
Covers risk-tier thresholds, abnormality scoring, risk flags,
explanation bullets, and recommendation mapping.
No trained model is loaded — these test deterministic logic only.

Run from the `presentations/` directory:
    cd presentations
    python -m pytest tests/
"""
import pytest

from services.prediction_service import get_risk_category
from services.explanation_service import (
    abnormality_score,
    get_risk_flags,
    build_explanation_bullets,
)
from services.recommendation_service import get_recommendations, get_why_text


# A baseline "healthy" patient — all values inside normal ranges.
def healthy_patient(**overrides):
    p = {
        'age': 50,
        'anaemia': 0,
        'creatinine_phosphokinase': 100,
        'diabetes': 0,
        'ejection_fraction': 60,
        'high_blood_pressure': 0,
        'platelets': 250000,
        'serum_creatinine': 1.0,
        'serum_sodium': 140,
        'sex': 1,
        'smoking': 0,
    }
    p.update(overrides)
    return p


# ── Risk categorisation (thresholds: HIGH=0.7, MEDIUM=0.4) ──────────────────────

class TestRiskCategory:
    def test_high(self):
        assert get_risk_category(0.85)['category'] == 'HIGH'

    def test_high_boundary(self):
        # 0.70 is inclusive → HIGH
        assert get_risk_category(0.70)['category'] == 'HIGH'

    def test_medium(self):
        assert get_risk_category(0.55)['category'] == 'MEDIUM'

    def test_medium_boundary(self):
        # 0.40 is inclusive → MEDIUM
        assert get_risk_category(0.40)['category'] == 'MEDIUM'

    def test_just_below_medium(self):
        assert get_risk_category(0.39)['category'] == 'LOW'

    def test_low(self):
        assert get_risk_category(0.10)['category'] == 'LOW'

    def test_returns_label_and_color(self):
        result = get_risk_category(0.9)
        assert result['label'] == 'High Risk'
        assert result['color'].startswith('#')


# ── Abnormality scoring ─────────────────────────────────────────────────────────

class TestAbnormalityScore:
    def test_normal_value_scores_zero(self):
        # ejection_fraction normal range is (55, 70), bad direction 'low'
        assert abnormality_score('ejection_fraction', 60) == 0.0

    def test_low_ef_is_abnormal(self):
        # 30 is below 55 → positive score in the 'bad' (low) direction
        assert abnormality_score('ejection_fraction', 30) > 0.0

    def test_high_creatinine_is_abnormal(self):
        # serum_creatinine range (0.7, 1.2), bad direction 'high'
        assert abnormality_score('serum_creatinine', 3.0) > 0.0

    def test_unknown_feature_scores_zero(self):
        assert abnormality_score('not_a_feature', 999) == 0.0


# ── Risk flags ──────────────────────────────────────────────────────────────────

class TestRiskFlags:
    def test_healthy_patient_no_flags(self):
        flags, _ = get_risk_flags(healthy_patient())
        assert flags == []

    def test_low_ejection_fraction_flagged(self):
        flags, _ = get_risk_flags(healthy_patient(ejection_fraction=30))
        flagged = [f for f, _ in flags]
        assert 'ejection_fraction' in flagged

    def test_diabetes_flagged(self):
        flags, _ = get_risk_flags(healthy_patient(diabetes=1))
        assert 'diabetes' in [f for f, _ in flags]

    def test_low_platelets_flagged(self):
        flags, _ = get_risk_flags(healthy_patient(platelets=50000))
        assert 'platelets' in [f for f, _ in flags]

    def test_high_platelets_flagged(self):
        flags, _ = get_risk_flags(healthy_patient(platelets=700000))
        assert 'platelets' in [f for f, _ in flags]


# ── Explanation bullets ─────────────────────────────────────────────────────────

class TestExplanationBullets:
    def test_healthy_patient_gets_fallback_message(self):
        bullets = build_explanation_bullets(healthy_patient(), prob=0.2)
        assert len(bullets) == 1
        assert 'No individual clinical values' in bullets[0]

    def test_low_ef_produces_bullet(self):
        bullets = build_explanation_bullets(
            healthy_patient(ejection_fraction=25), prob=0.8
        )
        assert any('ejection fraction' in b.lower() for b in bullets)

    def test_multiple_abnormals_produce_multiple_bullets(self):
        bullets = build_explanation_bullets(
            healthy_patient(ejection_fraction=25, serum_creatinine=3.0, diabetes=1),
            prob=0.9,
        )
        assert len(bullets) >= 3


# ── Recommendations ─────────────────────────────────────────────────────────────

class TestRecommendations:
    def test_high_tier(self):
        recs = get_recommendations('HIGH')
        assert len(recs) == 4

    def test_medium_tier(self):
        recs = get_recommendations('MEDIUM')
        assert len(recs) == 3

    def test_low_tier(self):
        recs = get_recommendations('LOW')
        assert len(recs) == 3

    def test_case_insensitive(self):
        assert get_recommendations('high') == get_recommendations('HIGH')

    def test_unknown_tier_defaults_to_low(self):
        assert get_recommendations('bogus') == get_recommendations('LOW')

    def test_why_text_higher_when_elevated(self):
        assert 'higher' in get_why_text(0.6)

    def test_why_text_lower_when_low(self):
        assert 'lower' in get_why_text(0.2)