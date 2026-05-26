import pandas as pd
import streamlit as st

from services.explanation_service import get_top_contributing_factors
from services.prediction_service import score_patient
from utils.constants import (
    BOOLEAN_FEATURES, DATA_PATH, FEATURE_LABELS, FEATURES, RISK_THRESHOLDS,
)
from utils.ui_components import (
    factor_bars_html, info_box, info_pill, render_page_header,
)


# ── Data loading ───────────────────────────────────────────────────────────────

def _load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df.insert(0, 'patient_id', [f'P{i:06d}' for i in range(len(df))])
    return df


# ── Patient selector row ───────────────────────────────────────────────────────

def _render_patient_selector(df: pd.DataFrame) -> pd.Series:
    sel_col, info1, info2, info3, info4 = st.columns([2, 1.2, 1.4, 1.6, 1.6])

    with sel_col:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">Select Patient</span>',
                    unsafe_allow_html=True)
        selected_id = st.selectbox(
            "Patient ID", df['patient_id'].tolist(),
            format_func=lambda x: f"Patient ID: {x}",
            label_visibility="collapsed",
        )

    patient_row  = df[df['patient_id'] == selected_id].iloc[0]
    patient_dict = patient_row[FEATURES].to_dict()
    actual       = int(patient_row['DEATH_EVENT'])
    sex_label    = "Male" if patient_dict['sex'] == 1 else "Female"

    prob, risk_category = score_patient(patient_dict)
    rc = risk_category['color']

    outcome_color = "#f85149" if actual == 1 else "#3fb950"
    outcome_text  = ("Deceased During Follow-Up" if actual == 1
                     else "Survived Follow-Up")

    with info1:
        st.markdown(info_pill("👤 Age / Sex",
                              f"{int(patient_dict['age'])} / {sex_label}"),
                    unsafe_allow_html=True)
    with info2:
        st.markdown(info_pill("📅 Follow-up Time",
                              f"{int(patient_row['time'])} days"),
                    unsafe_allow_html=True)
    with info3:
        st.markdown(info_pill("❤️ Historical Outcome", outcome_text,
                              value_color=outcome_color),
                    unsafe_allow_html=True)
    with info4:
        st.markdown(info_pill("🛡️ Predicted Risk Level", risk_category['label'],
                              value_color=rc,
                              sub=f"Probability: {prob:.2f} ({prob * 100:.0f}%)"),
                    unsafe_allow_html=True)

    return patient_row, patient_dict, actual, prob, risk_category


# ── Patient details table ──────────────────────────────────────────────────────

def _patient_table_html(patient_dict: dict) -> str:
    rows = ""
    for feature, label in FEATURE_LABELS.items():
        val = patient_dict[feature]
        if feature == 'sex':
            display = "Male" if val == 1 else "Female"
        elif feature in BOOLEAN_FEATURES:
            display = "Yes" if val == 1 else "No"
        elif feature == 'platelets':
            display = f"{val / 1000:.0f}"
        else:
            display = str(val)
        rows += f"<tr><td>{label}</td><td><b style='color:#e6edf3;'>{display}</b></td></tr>"

    return f"""
    <div class="section-card">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
            <span style="font-size:1rem;">📋</span>
            <span style="font-weight:600;color:#e6edf3;">Patient Details (Clinical Indicators)</span>
        </div>
        <table class="styled-table">
            <thead><tr><th>Indicator</th><th>Value</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        <div class="info-box" style="margin-top:0.75rem;">
            ℹ️ These values are from the historical dataset.
        </div>
    </div>"""


# ── Contributing factors ───────────────────────────────────────────────────────

def _contributing_factors_html(patient_dict: dict) -> str:
    top_features, total = get_top_contributing_factors(patient_dict)
    bars = factor_bars_html(top_features, total, FEATURE_LABELS)
    return f"""
    <div style="margin-top:1rem;">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
            <span style="font-size:1rem;">🔬</span>
            <span style="font-weight:600;color:#3fb950;">Top Contributing Risk Factors</span>
        </div>
        {bars}
        <div style="font-size:0.75rem;color:#6e7681;margin-top:0.25rem;font-style:italic;">
            Percentages indicate relative contribution to the predicted risk.
        </div>
    </div>"""


# ── Risk assessment panel ──────────────────────────────────────────────────────

def _risk_assessment_html(patient_dict: dict, prob: float,
                           risk_category: dict) -> str:
    rc   = risk_category['color']
    tier = risk_category['category']
    elevation = "elevated" if prob >= RISK_THRESHOLDS["MEDIUM"] else "lower"
    risk_str  = ("high-risk"     if prob >= RISK_THRESHOLDS["HIGH"]
                 else "moderate-risk" if prob >= RISK_THRESHOLDS["MEDIUM"]
                 else "low-risk")

    return f"""
    <div class="section-card">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">
            <span style="font-size:1rem;">🛡️</span>
            <span style="font-weight:600;color:#e6edf3;">Risk Assessment</span>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;
             text-align:center;margin-bottom:1rem;">
            <div>
                <div style="font-size:0.7rem;font-weight:600;color:#8b949e;
                     text-transform:uppercase;letter-spacing:0.04em;margin-bottom:0.4rem;">
                     Predicted Risk Score</div>
                <div style="font-size:2.2rem;font-weight:700;color:{rc};line-height:1;">{prob:.2f}</div>
                <div style="font-size:0.9rem;color:{rc};font-weight:600;">({prob * 100:.0f}%)</div>
                <div style="font-size:0.72rem;color:#6e7681;margin-top:0.4rem;">
                    Probability of adverse outcome<br>(DEATH_EVENT = 1)</div>
            </div>
            <div>
                <div style="font-size:0.7rem;font-weight:600;color:#8b949e;
                     text-transform:uppercase;letter-spacing:0.04em;margin-bottom:0.4rem;">
                     Risk Category</div>
                <div style="background:{rc}22;border:1px solid {rc}66;border-radius:8px;
                     padding:0.5rem;margin:0.4rem 0;">
                    <span style="color:{rc};font-weight:700;font-size:0.88rem;">
                        ⚠️ {risk_category['label'].upper()}
                    </span>
                </div>
                <div style="font-size:0.72rem;color:#6e7681;">Elevated risk of adverse outcome.</div>
            </div>
            <div>
                <div style="font-size:0.7rem;font-weight:600;color:#8b949e;
                     text-transform:uppercase;letter-spacing:0.04em;margin-bottom:0.4rem;">
                     Interpretation</div>
                <div style="font-size:0.8rem;color:#c9d1d9;line-height:1.5;margin-top:0.4rem;">
                    The patient's clinical indicators resemble patterns associated with {elevation}
                    adverse outcome risk in the historical dataset.
                </div>
            </div>
        </div>
    </div>"""


# ── Historical case interpretation ────────────────────────────────────────────

def _case_interpretation_html(patient_dict: dict, actual: int,
                               prob: float, risk_category: dict) -> str:
    ef_val  = patient_dict['ejection_fraction']
    sc_val  = patient_dict['serum_creatinine']
    sn_val  = patient_dict['serum_sodium']
    age_val = int(patient_dict['age'])

    key_drivers = []
    if ef_val < 40:
        key_drivers.append(f"reduced ejection fraction ({ef_val}%)")
    if sc_val > 1.2:
        key_drivers.append(f"elevated serum creatinine ({sc_val} mg/dL)")
    if age_val > 60:
        key_drivers.append(f"advanced age ({age_val} years)")
    if sn_val < 135:
        key_drivers.append(f"low serum sodium ({sn_val} mEq/L)")
    key_driver_str = (", ".join(key_drivers[:3]) if key_drivers
                      else "the combined clinical profile")

    comorbidities = []
    if patient_dict['high_blood_pressure'] == 1:
        comorbidities.append("hypertension")
    if patient_dict['diabetes'] == 1:
        comorbidities.append("diabetes")
    if patient_dict['anaemia'] == 1:
        comorbidities.append("anaemia")
    if patient_dict['smoking'] == 1:
        comorbidities.append("smoking history")

    elevation_str = "elevated" if prob >= RISK_THRESHOLDS["MEDIUM"] else "predicted"
    risk_level_str = ("high-risk"     if prob >= RISK_THRESHOLDS["HIGH"]
                      else "moderate-risk" if prob >= RISK_THRESHOLDS["MEDIUM"]
                      else "low-risk")
    outcome_context = ("This patient experienced an adverse outcome during the follow-up period."
                       if actual == 1
                       else "This patient survived the follow-up period without an adverse outcome.")

    def _badge(letter, color):
        return (f'<div style="background:{color};border-radius:50%;width:22px;height:22px;'
                f'display:flex;align-items:center;justify-content:center;flex-shrink:0;'
                f'margin-top:2px;"><span style="font-size:0.65rem;font-weight:700;'
                f'color:#fff;">{letter}</span></div>')

    key_block = (
        '<div style="display:flex;gap:0.75rem;align-items:flex-start;">'
        + _badge('K', '#f85149')
        + f'<div style="font-size:0.83rem;color:#c9d1d9;line-height:1.5;">'
          f'<b style="color:#f85149;">Key Driver:</b> {key_driver_str.capitalize()} '
          f'contributed most to the {elevation_str} risk.</div></div>'
    )

    comorbidity_block = ""
    if comorbidities:
        comorbidity_str = " and ".join(comorbidities)
        if prob >= RISK_THRESHOLDS["MEDIUM"]:
            sentence = f"History of {comorbidity_str} further increases overall risk."
        else:
            sentence = f"History of {comorbidity_str} also contributes to the overall risk profile."
        comorbidity_block = (
            '<div style="display:flex;gap:0.75rem;align-items:flex-start;">'
            + _badge('C', '#e3b341')
            + f'<div style="font-size:0.83rem;color:#c9d1d9;line-height:1.5;">'
              f'<b style="color:#e3b341;">Comorbidity Impact:</b> {sentence}</div></div>'
        )

    outcome_block = (
        '<div style="display:flex;gap:0.75rem;align-items:flex-start;">'
        + _badge('O', '#58a6ff')
        + f'<div style="font-size:0.83rem;color:#c9d1d9;line-height:1.5;">'
          f'<b style="color:#58a6ff;">Outcome Context:</b> {outcome_context}</div></div>'
    )

    return f"""
    <div class="section-card" style="margin-top:1rem;">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
            <span style="font-size:1rem;">🔍</span>
            <span style="font-weight:600;color:#e6edf3;">Historical Case Interpretation</span>
        </div>
        <p style="font-size:0.85rem;color:#8b949e;margin:0 0 0.75rem 0;">
            Based on the provided clinical indicators, the model identified patterns commonly
            associated with {risk_level_str} outcomes in similar historical cases.
        </p>
        <div style="display:flex;flex-direction:column;gap:0.6rem;">
            {key_block}{comorbidity_block}{outcome_block}
        </div>
        <p style="font-size:0.75rem;color:#6e7681;margin:0.75rem 0 0 0;font-style:italic;">
            This section provides retrospective interpretation and is <u>not</u> a recommendation
            for clinical action.
        </p>
    </div>"""


# ── Patient summary ────────────────────────────────────────────────────────────

def _patient_summary_html(patient_dict: dict, actual: int, prob: float,
                           sex_label: str) -> str:
    ef_val  = patient_dict['ejection_fraction']
    sc_val  = patient_dict['serum_creatinine']
    sn_val  = patient_dict['serum_sodium']
    age_val = int(patient_dict['age'])

    diab = "diabetes" if patient_dict['diabetes'] == 1 else ""
    hbp  = "hypertension" if patient_dict['high_blood_pressure'] == 1 else ""
    comor = " and ".join(filter(None, [diab, hbp]))
    comor_sent = f" History of {comor} further increased overall risk." if comor else ""

    if actual == 1 and prob >= RISK_THRESHOLDS['MEDIUM']:
        outcome_sent = ("The model predicted high risk of adverse outcome, which was consistent "
                        "with the observed historical outcome.")
    elif actual == 0 and prob < RISK_THRESHOLDS['MEDIUM']:
        outcome_sent = ("The model predicted lower risk, and the patient survived "
                        "the follow-up period.")
    else:
        predicted = "high" if prob >= RISK_THRESHOLDS['MEDIUM'] else "low"
        observed  = "adverse" if actual == 1 else "survival"
        outcome_sent = f"The model predicted {predicted} risk; the observed outcome was {observed}."

    return f"""
    <div class="section-card" style="margin-top:1rem;">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
            <span style="font-size:1rem;">📄</span>
            <span style="font-weight:600;color:#e6edf3;">Patient Summary</span>
        </div>
        <div style="font-size:0.85rem;color:#c9d1d9;line-height:1.7;">
            This {age_val}-year-old {sex_label.lower()} had a reduced ejection fraction of {ef_val}%,
            serum creatinine of {sc_val} mg/dL, and serum sodium of {sn_val} mEq/L.{comor_sent}
            {outcome_sent}
        </div>
        <div class="info-box" style="margin-top:0.75rem;">
            ℹ️ This page is for educational and research purposes only and does not provide
            clinical advice.
        </div>
    </div>"""


# ── Public entry point ─────────────────────────────────────────────────────────

def render() -> None:
    render_page_header(
        "Patient Review",
        "Review historical patient cases to understand risk predictions, "
        "key indicators, and outcomes.",
    )

    df = _load_dataset()
    patient_row, patient_dict, actual, prob, risk_category = _render_patient_selector(df)
    sex_label = "Male" if patient_dict['sex'] == 1 else "Female"

    st.markdown("<br>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1.1])

    with left_col:
        st.markdown(_patient_table_html(patient_dict), unsafe_allow_html=True)
        st.markdown(_contributing_factors_html(patient_dict), unsafe_allow_html=True)

    with right_col:
        st.markdown(_risk_assessment_html(patient_dict, prob, risk_category),
                    unsafe_allow_html=True)
        st.markdown(_case_interpretation_html(patient_dict, actual, prob, risk_category),
                    unsafe_allow_html=True)
        st.markdown(_patient_summary_html(patient_dict, actual, prob, sex_label),
                    unsafe_allow_html=True)