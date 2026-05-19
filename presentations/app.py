import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Heart Failure Prediction", layout="wide")

def kpi_card(label: str, value: str, color: str = "#4B9EFF", help: str = "") -> str:
    return f"""
        <div style="
            background-color: #1e1e2e;
            border-left: 4px solid {color};
            border-radius: 12px;
            padding: 20px 24px;
            margin: 4px;
        ">
            <p style="margin:0; font-size:0.85rem; color:#aaaacc;">{label}</p>
            <p style="margin:4px 0 0 0; font-size:2rem; font-weight:700; color:#ffffff;">{value}</p>
            <p style="margin:4px 0 0 0; font-size:0.75rem; color:#888899;">{help}</p>
        </div>
    """

page = st.sidebar.selectbox("Navigate", ["Dashboard", "Model Metrics", "Patient Prediction", "Feature Importance"])
st.sidebar.divider()
st.sidebar.warning("**DISCLAIMER**: This tool is for educational/demo use and should not be taken as medical advice")

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
METRICS_PATH = os.path.join(BASE_DIR, '..', 'notebooks', 'metrics.csv')
IMPORTANCE_PATH = os.path.join(BASE_DIR, '..', 'notebooks', 'feature_importance.csv')
PREDICTIONS_PATH = os.path.join(BASE_DIR, '..', 'notebooks', 'predictions.csv')

RISK_THRESHOLDS = {
    "HIGH":   0.7,
    "MEDIUM": 0.4,
}

RISK_LABELS = {
    "HIGH":   "High Risk",
    "MEDIUM": "Medium Risk",
    "LOW":    "Low Risk",
}

RISK_URGENCY = {
    "HIGH":   "critical",
    "MEDIUM": "moderate",
    "LOW":    "low",
}

RISK_COLORS = {
    "HIGH":   "#FF4B4B",
    "MEDIUM": "#FFA500",
    "LOW":    "#00C853",
}

if page == "Dashboard":
    st.title("Heart Failure — Patient Dashboard")
    st.caption("Summary statistics derived from model predictions on the full dataset.")

    predictions_df = pd.read_csv(PREDICTIONS_PATH)

    # ── Backend Calculations ──────────────────────────────────────────────
    patient_count      = len(predictions_df)
    observed_mortality = predictions_df['DEATH_EVENT'].mean() * 100
    high_risk_count    = (predictions_df['probability'] >= RISK_THRESHOLDS['HIGH']).sum()
    avg_predicted_risk = predictions_df['probability'].mean() * 100

    # ── KPI Cards ─────────────────────────────────────────────────────────
    st.subheader("Overview")
    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(kpi_card("Total Patients",      f"{patient_count:,}",          "#4B9EFF"), unsafe_allow_html=True)
    col2.markdown(kpi_card("Observed Mortality",  f"{observed_mortality:.1f}%",  "#FFA500"), unsafe_allow_html=True)
    col3.markdown(kpi_card("High Risk Patients",  f"{high_risk_count:,}",        "#FF4B4B", f"{high_risk_count / patient_count * 100:.1f}% of total"), unsafe_allow_html=True)
    col4.markdown(kpi_card("Avg Predicted Risk",  f"{avg_predicted_risk:.1f}%",  "#A855F7", "Mean probability across all patients"), unsafe_allow_html=True)

    st.divider()
    st.subheader("Risk Distribution")

    low_count    = (predictions_df['probability'] <  RISK_THRESHOLDS['MEDIUM']).sum()
    medium_count = (predictions_df['probability'] >= RISK_THRESHOLDS['MEDIUM']).sum() - high_risk_count

    risk_col1, risk_col2, risk_col3 = st.columns(3)

    risk_col1.markdown(kpi_card("Low Risk",    f"{low_count:,}",       "#00C853", f"{low_count / patient_count * 100:.1f}% of total"),    unsafe_allow_html=True)
    risk_col2.markdown(kpi_card("Medium Risk", f"{medium_count:,}",    "#FFA500", f"{medium_count / patient_count * 100:.1f}% of total"), unsafe_allow_html=True)
    risk_col3.markdown(kpi_card("High Risk",   f"{high_risk_count:,}", "#FF4B4B", f"{high_risk_count / patient_count * 100:.1f}% of total"),   unsafe_allow_html=True)


elif page == "Patient Prediction":
    st.title("Patient Prediction")
    st.caption("Select a patient to review their profile, predicted risk, and clinical recommendation.")

    import pickle
    import sys
    sys.path.append(os.path.join(BASE_DIR, '..', 'notebooks'))

    PIPELINE_PATH     = os.path.join(BASE_DIR, '..', 'notebooks', 'pipeline.pkl')
    TRAINING_DATA_PATH = os.path.join(BASE_DIR, '..', 'notebooks', 'training_data.csv')  # if used by survival

    predictions_df = pd.read_csv(PREDICTIONS_PATH)
    df_full        = pd.read_csv(os.path.join(BASE_DIR, '..', 'data', 'heart_failure_clinical_records_dataset.csv'))

    # Re-attach patient_id to full data
    df_full.insert(0, 'patient_id', [f'P{i:06d}' for i in range(len(df_full))])

    with open(PIPELINE_PATH, 'rb') as f:
        pipeline = pickle.load(f)

    FEATURES = [
        'age', 'anaemia', 'creatinine_phosphokinase', 'diabetes',
        'ejection_fraction', 'high_blood_pressure', 'platelets',
        'serum_creatinine', 'serum_sodium', 'sex', 'smoking'
    ]

    FEATURE_LABELS = {
        'age':                      'Age',
        'anaemia':                  'Anaemia',
        'creatinine_phosphokinase': 'CPK (U/L)',
        'ejection_fraction':        'Ejection Fraction (%)',
        'diabetes':                 'Diabetes',
        'high_blood_pressure':      'High Blood Pressure',
        'platelets':                'Platelets (/µL)',
        'serum_creatinine':         'Serum Creatinine (mg/dL)',
        'serum_sodium':             'Serum Sodium (mEq/L)',
        'sex':                      'Sex',
        'smoking':                  'Smoking',
    }

    BOOLEAN_FEATURES = {
        'anaemia', 'diabetes', 'high_blood_pressure', 'smoking'
    }

    def get_risk_category(prob):
        if prob >= RISK_THRESHOLDS['HIGH']:
            return {"category": "HIGH", "label": "High Risk",   "color": RISK_COLORS['HIGH']}
        elif prob >= RISK_THRESHOLDS['MEDIUM']:
            return {"category": "MEDIUM", "label": "Medium Risk", "color": RISK_COLORS['MEDIUM']}
        else:
            return {"category": "LOW",  "label": "Low Risk",    "color": RISK_COLORS['LOW']}

    # ── Patient Selector ──────────────────────────────────────────────────
    patient_ids = df_full['patient_id'].tolist()
    selected_id = st.selectbox("Select Patient ID", patient_ids)

    patient_row  = df_full[df_full['patient_id'] == selected_id].iloc[0]
    patient_dict = patient_row[FEATURES].to_dict()

    prob          = pipeline.predict_proba(pd.DataFrame([patient_dict])[FEATURES])[0][1]
    risk_category = get_risk_category(prob)
    actual        = int(patient_row['DEATH_EVENT'])

    st.divider()

    # ── Row 1 — Risk Summary ──────────────────────────────────────────────
    st.subheader("Risk Summary")
    sum_col1, sum_col2, sum_col3 = st.columns(3)

    sum_col1.markdown(kpi_card(
        "Predicted Mortality Risk",
        f"{prob * 100:.1f}%",
        risk_category['color']
    ), unsafe_allow_html=True)

    sum_col2.markdown(kpi_card(
        "Risk Category",
        risk_category['label'],
        risk_category['color']
    ), unsafe_allow_html=True)

    sum_col3.markdown(kpi_card(
        "Actual Outcome",
        "Died" if actual == 1 else "Survived",
        "#FF4B4B" if actual == 1 else "#00C853"
    ), unsafe_allow_html=True)

    st.divider()

    # ── Row 2 — Patient Profile + Risk Factors ────────────────────────────
    profile_col, factors_col = st.columns([1, 1])

    with profile_col:
        st.subheader("Patient Profile")
        profile_rows = []
        for feature, label in FEATURE_LABELS.items():
            value = patient_dict[feature]
            if feature == 'sex':
                display = "Male" if value == 1 else "Female"
            elif feature in BOOLEAN_FEATURES:
                display = "Yes" if value == 1 else "No"
            elif feature == 'platelets':
                display = f"{value:,.0f}"
            else:
                display = str(value)
            profile_rows.append({"Feature": label, "Value": display})

        st.dataframe(
            pd.DataFrame(profile_rows).set_index('Feature'),
            use_container_width=True
        )

    with factors_col:
        st.subheader("Top Risk Factors")

        # Inline risk factor logic (mirrors notebook get_risk_factors)
        try:
            importance_df  = pd.read_csv(IMPORTANCE_PATH)
            importance_map = dict(zip(importance_df['Feature'], importance_df['Importance']))
        except FileNotFoundError:
            importance_map = {}

        flags = {}
        if patient_dict['ejection_fraction'] < 40:
            flags['ejection_fraction'] = f"Low ejection fraction ({patient_dict['ejection_fraction']}%) — heart pumping below normal range"
        if patient_dict['serum_creatinine'] > 2.0:
            flags['serum_creatinine'] = f"Elevated serum creatinine ({patient_dict['serum_creatinine']} mg/dL) — above normal range"
        if patient_dict['age'] > 70:
            flags['age'] = f"Age {int(patient_dict['age'])} — older age associated with higher cardiac risk"
        if patient_dict['serum_sodium'] < 130:
            flags['serum_sodium'] = f"Low serum sodium ({patient_dict['serum_sodium']} mEq/L) — below normal range"
        if patient_dict['diabetes'] == 1:
            flags['diabetes'] = "Diabetes present — associated with increased cardiovascular risk"
        if patient_dict['high_blood_pressure'] == 1:
            flags['high_blood_pressure'] = "High blood pressure — associated with increased cardiac strain"
        if patient_dict['anaemia'] == 1:
            flags['anaemia'] = "Anaemia present — associated with reduced oxygen delivery"
        if patient_dict['creatinine_phosphokinase'] > 1000:
            flags['creatinine_phosphokinase'] = f"Elevated CPK ({patient_dict['creatinine_phosphokinase']} U/L) — above normal range"
        if patient_dict['smoking'] == 1:
            flags['smoking'] = "Smoking present — associated with accelerated arterial damage"
        if patient_dict['platelets'] < 100000:
            flags['platelets'] = f"Low platelets ({patient_dict['platelets']:,.0f}/µL) — below normal range"
        elif patient_dict['platelets'] > 600000:
            flags['platelets'] = f"High platelets ({patient_dict['platelets']:,.0f}/µL) — above normal range"

        if flags:
            ranked = sorted(
                flags.items(),
                key=lambda x: importance_map.get(x[0], 0),
                reverse=True
            )
            for feature, description in ranked:
                st.markdown(
                    f"<div style='"
                    f"border-left: 4px solid {risk_category['color']};"
                    f"padding: 8px 12px;"
                    f"margin-bottom: 8px;"
                    f"background-color: #1e1e2e;"
                    f"border-radius: 0 8px 8px 0;'>"
                    f"<strong>{FEATURE_LABELS.get(feature, feature)}</strong><br/>"
                    f"<span style='font-size:0.85rem;color:#aaaacc;'>{description}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.success("No individual risk factors flagged for this patient.")

    st.divider()

    # ── Row 3 — Recommendation ────────────────────────────────────────────
    st.subheader("Clinical Recommendation")

    category = risk_category['category']
    color    = risk_category['color']

    if category == "HIGH":
        title  = "⛔ Admit Immediately"
        action = "Immediate admission and intervention is strongly recommended. Do not discharge without cardiology review."
    elif category == "MEDIUM":
        title  = "⚠️ Monitor Closely"
        action = "Schedule follow-up within 7 days. Monitor serum creatinine and ejection fraction closely. Consider cardiology referral."
    else:
        title  = "✅ Routine Care"
        action = "Continue routine monitoring. Reassess if symptoms worsen or new risk factors emerge."

    st.markdown(
        f"<div style='"
        f"border-left: 6px solid {color};"
        f"background-color: #1e1e2e;"
        f"border-radius: 0 12px 12px 0;"
        f"padding: 20px 24px;'>"
        f"<h4 style='margin:0;color:{color};'>{title}</h4>"
        f"<p style='margin:8px 0 0 0;color:#cccccc;'>{action}</p>"
        f"</div>",
        unsafe_allow_html=True
    )


elif page == "Model Metrics":
    st.title("Model Metrics")
    st.caption("Repeated Stratified K-Fold (5 splits x 10 repeats = 50 evaluations)")

    metrics_df = pd.read_csv(METRICS_PATH)

    # Split overfitting gap out from the main metrics
    gap_row     = metrics_df[metrics_df['Metric'] == 'Overfitting Gap']
    metrics_df  = metrics_df[metrics_df['Metric'] != 'Overfitting Gap']

    # --- KPI cards for Mean scores ---
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)

    for col, row in zip(
        [col1, col2, col3],
        metrics_df.itertuples()
    ):
        col.metric(label=row.Metric, value=f"{row.Mean:.3f}")
    
    # --- Overfitting gap ---
    gap = gap_row['Mean'].values[0]
    st.metric(
        label="Overfitting Gap (train - test)",
        value=f"{gap:.3f}"
    )

    st.divider()

    # --- Full metrics table ---
    st.subheader("Full Cross-Validation Results")
    st.dataframe(
        metrics_df.set_index('Metric'),
        use_container_width=True
    )

    
elif page == "Feature Importance":
    st.title("Feature Importance")
    st.caption(
        "Shows how much each clinical feature contributed to the model's "
        "predictions, based on Gini impurity reduction across all decision "
        "trees. A higher value means the feature was used more often to "
        "separate high-risk from low-risk patients."
    )

    # Disclaimer
    st.info(
        "⚠️ These importances reflect patterns in the training data only. "
        "They indicate statistical association, not clinical causation. "
        "Do not interpret them as medical recommendations."
    )

    importance_df = pd.read_csv(IMPORTANCE_PATH)

    # KPI — top feature
    top_feature = importance_df.iloc[0]
    st.metric(
        label="Most Influential Feature",
        value=top_feature['Feature'],
        delta=f"Importance: {top_feature['Importance']:.4f}"
    )

    st.divider()

    # Chart
    import plotly.express as px

    fig = px.bar(
        importance_df.sort_values('Importance'),
        x='Importance',
        y='Feature',
        orientation='h',
        color='Importance',
        color_continuous_scale=['#00C853', '#FFA500', '#FF4B4B'],
        title='Feature Importance — Random Forest'
    )
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis_title=None,
        xaxis_title='Importance (Gini impurity reduction)'
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Table
    st.subheader("Full Importance Table")
    st.dataframe(
        importance_df.set_index('Rank'),
        use_container_width=True
    )