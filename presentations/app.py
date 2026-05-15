import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Heart Failure Prediction", layout="wide")
page = st.sidebar.selectbox("Navigate", ["Model Metrics", "Patient Prediction"])

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
METRICS_PATH = os.path.join(BASE_DIR, '..', 'notebooks', 'metrics.csv')

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


if page == "Model Metrics":
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