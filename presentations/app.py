import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Heart Failure Prediction", layout="wide")
page = st.sidebar.selectbox("Navigate", ["Model Metrics", "Patient Prediction", "Feature Importance"])
st.sidebar.divider()
st.sidebar.warning("**DISCLAIMER**: This tool is for educational/demo use and should not be taken as medical advice")

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
METRICS_PATH = os.path.join(BASE_DIR, '..', 'notebooks', 'metrics.csv')
IMPORTANCE_PATH = os.path.join(BASE_DIR, '..', 'notebooks', 'feature_importance.csv')

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