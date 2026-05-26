import streamlit as st

from services.explanation_service import (
    build_explanation_bullets,
    get_top_contributing_factors,
)
from services.prediction_service import score_patient
from services.recommendation_service import get_recommendations, get_why_text
from utils.constants import FEATURE_LABELS, RISK_THRESHOLDS
from utils.ui_components import factor_bars_html, render_page_header


# ── Patient input form ─────────────────────────────────────────────────────────

def _render_input_form():
    st.markdown('<span style="color:#e6edf3;font-weight:600;">1. Enter Patient Indicators</span>',
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    age       = st.number_input("👤 Age (years)",                    min_value=1,   max_value=120, value=65)
    anaemia   = st.selectbox("🩸 Anaemia",                           ["No", "Yes"])
    diabetes  = st.selectbox("🩸 Diabetes",                          ["No", "Yes"])
    ef        = st.number_input("❤️ Ejection Fraction (%)",         min_value=1,   max_value=100, value=38)
    sc        = st.number_input("🩺 Serum Creatinine (mg/dL)",      min_value=0.1, max_value=20.0, value=1.1, step=0.1)
    sn        = st.number_input("💧 Serum Sodium (mEq/L)",          min_value=100, max_value=160, value=136)
    hbp       = st.selectbox("❤️ High Blood Pressure",               ["No", "Yes"])
    smoking   = st.selectbox("🚬 Smoking",                           ["No", "Yes"])
    platelets = st.number_input("🔬 Platelets (kiloplatelets/mL)",   min_value=1,   max_value=1000, value=250)
    cpk       = st.number_input("⚙️ Creatinine Phosphokinase (U/L)", min_value=1,   max_value=10000, value=200)
    sex       = st.selectbox("⚧ Sex",                                ["Female", "Male"])

    st.markdown('<div class="info-box" style="margin-top:1rem;">'
                'ℹ️ Inputs are for demonstration only and are not saved.</div>',
                unsafe_allow_html=True)

    col_r, col_p = st.columns(2)
    col_r.button("↺ Reset")
    col_p.button("Predict Risk →", type="primary")

    return dict(
        age=float(age),
        anaemia=1 if anaemia == "Yes" else 0,
        creatinine_phosphokinase=int(cpk),
        diabetes=1 if diabetes == "Yes" else 0,
        ejection_fraction=int(ef),
        high_blood_pressure=1 if hbp == "Yes" else 0,
        platelets=float(platelets * 1000),
        serum_creatinine=float(sc),
        serum_sodium=int(sn),
        sex=1 if sex == "Male" else 0,
        smoking=1 if smoking == "Yes" else 0,
    ), dict(age=age, ef=ef, sc=sc, sn=sn, diabetes=diabetes, anaemia=anaemia,
            hbp=hbp, smoking=smoking, sex=sex, platelets=platelets, cpk=cpk)


# ── Risk assessment panel ──────────────────────────────────────────────────────

def _render_risk_panel(patient_dict: dict, prob: float, risk_category: dict) -> None:
    rc = risk_category['color']

    top_features, total = get_top_contributing_factors(patient_dict)
    bars = factor_bars_html(top_features, total, FEATURE_LABELS)
    factors_note = ("Based on model importance × how abnormal this patient's values are.")
    elevation = "elevated" if prob >= RISK_THRESHOLDS["MEDIUM"] else "lower"

    st.markdown(f"""
    <div class="section-card">
        <span style="color:#e6edf3;font-weight:600;">2. Risk Assessment</span>
        <div style="text-align:center;padding:1.5rem 0 1rem 0;">
            <div style="font-size:3rem;font-weight:700;color:{rc};line-height:1;">{prob:.2f}</div>
            <div style="font-size:1.25rem;font-weight:600;color:{rc};">{prob * 100:.0f}%</div>
            <div style="font-size:0.8rem;color:#6e7681;margin-top:0.5rem;">
                Higher score = higher risk of adverse outcome.
            </div>
        </div>
        <div style="background:{rc}18;border:1px solid {rc}44;border-radius:8px;
             padding:0.75rem;text-align:center;margin-bottom:1rem;">
            <span style="color:{rc};font-weight:700;font-size:1.1rem;">
                ⚠️ {risk_category['label'].upper()}
            </span>
        </div>
        <div class="info-box">ℹ️ This profile matches historical patients with {elevation}
        short-term adverse outcomes.</div>
        <div style="margin-top:1rem;">
            <span style="color:#e6edf3;font-weight:600;font-size:0.9rem;">
                Top Contributing Factors
            </span>
            <div style="margin-top:0.5rem;">
                {bars}
                <div style="font-size:0.75rem;color:#6e7681;margin-top:0.25rem;">
                    {factors_note}
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Prediction explanation
    bullets     = build_explanation_bullets(patient_dict, prob)
    bullets_html = "".join(
        f"<li style='margin-bottom:0.5rem;font-size:0.83rem;color:#c9d1d9;"
        f"line-height:1.5;'>{line}</li>"
        for line in bullets
    )
    direction = "higher" if prob >= RISK_THRESHOLDS["MEDIUM"] else "lower"
    st.markdown(f"""
    <div style="background:#1a1030;border:1px solid #bc8cff44;border-radius:8px;
         padding:1rem 1.25rem;margin-top:1rem;">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
            <span style="font-size:1rem;">🔍</span>
            <span style="font-weight:600;color:#bc8cff;font-size:0.9rem;">Prediction Explanation</span>
        </div>
        <p style="font-size:0.83rem;color:#8b949e;margin:0 0 0.6rem 0;">
            This prediction was influenced primarily by the following clinical indicators:
        </p>
        <ul style="margin:0;padding-left:1.25rem;">{bullets_html}</ul>
        <p style="font-size:0.78rem;color:#6e7681;margin:0.75rem 0 0 0;font-style:italic;">
            These factors have been associated with {direction} rates of adverse outcomes
            in similar historical patients.
        </p>
    </div>""", unsafe_allow_html=True)


# ── Recommendation panel ───────────────────────────────────────────────────────

def _render_recommendation(patient_dict: dict, prob: float,
                            risk_category: dict, form_vals: dict) -> None:
    rc   = risk_category['color']
    cat  = risk_category['category']

    bullets     = get_recommendations(cat)
    why_text    = get_why_text(prob)
    bullets_html = "".join(
        f"<li style='margin-bottom:0.4rem;font-size:0.85rem;color:#c9d1d9;'>{b}</li>"
        for b in bullets
    )

    fv = form_vals
    st.markdown(f"""
    <div style="background:{rc}18;border:1px solid {rc}44;border-radius:8px;
         padding:1rem;margin:0.75rem 0;">
        <div style="font-weight:600;color:{rc};margin-bottom:0.5rem;">⚠️ Recommended Action</div>
        <p style="font-size:0.85rem;margin:0 0 0.5rem 0;color:#c9d1d9;">Patient is at
            <b style="color:{rc};">{risk_category['label'].upper()}</b>.</p>
        <ul style="margin:0;padding-left:1.25rem;">{bullets_html}</ul>
    </div>

    <div style="background:#1c1a10;border:1px solid #e3b34133;border-radius:8px;
         padding:1rem;margin-bottom:0.75rem;">
        <div style="font-weight:600;color:#e3b341;margin-bottom:0.4rem;">💡 Why This Recommendation?</div>
        <div style="font-size:0.82rem;color:#c9d1d9;">{why_text}</div>
    </div>

    <div style="background:#12261e;border:1px solid #3fb95033;border-radius:8px;
         padding:1rem;margin-bottom:0.75rem;">
        <div style="font-weight:600;color:#3fb950;margin-bottom:0.4rem;">🛡️ Disclaimer</div>
        <div style="font-size:0.82rem;color:#c9d1d9;">This recommendation is generated by an AI
        model and is intended for decision-support and educational purposes only.
        Not a substitute for clinical judgment.</div>
    </div>

    <div style="background:#21262d;border:1px solid #30363d;border-radius:8px;padding:1rem;">
        <div style="font-weight:600;color:#e6edf3;margin-bottom:0.4rem;">📄 Input Summary</div>
        <div style="font-size:0.8rem;color:#8b949e;line-height:1.7;">
            Age: {fv['age']}, EF: {fv['ef']}%, Creatinine: {fv['sc']},
            Sodium: {fv['sn']},<br>
            Diabetes: {fv['diabetes']}, Anaemia: {fv['anaemia']},
            BP: {fv['hbp']}, Smoking: {fv['smoking']},<br>
            Sex: {fv['sex']}, Platelets: {fv['platelets']}k/mL,
            CPK: {fv['cpk']} U/L
        </div>
    </div>""", unsafe_allow_html=True)


# ── Public entry point ─────────────────────────────────────────────────────────

def render() -> None:
    render_page_header(
        "Simulated Patient Assessment",
        "Enter patient clinical indicators to estimate risk and receive recommendation.",
    )

    col_form, col_risk, col_rec = st.columns([1, 1, 1])

    with col_form:
        patient_dict, form_vals = _render_input_form()

    prob, risk_category = score_patient(patient_dict)

    with col_risk:
        _render_risk_panel(patient_dict, prob, risk_category)

    with col_rec:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">3. Recommendation</span>',
                    unsafe_allow_html=True)
        _render_recommendation(patient_dict, prob, risk_category, form_vals)