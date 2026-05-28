import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.constants import (
    IMPORTANCE_PATH, METRICS_PATH, PREDICTIONS_PATH,
    FEATURE_LABELS, PLOTLY_LAYOUT, RISK_THRESHOLDS,
)
from utils.ui_components import (
    info_box, kpi_card, render_footer, render_page_header,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _metric(metrics_df: pd.DataFrame, name: str) -> float:
    row = metrics_df[metrics_df['Metric'] == name]
    return float(row['Mean'].values[0]) if len(row) else 0.0


# ── Sub-sections ───────────────────────────────────────────────────────────────

def _render_kpi_row(predictions_df, accuracy_val, patient_count,
                    elevated_count, observed_mortality, observed_count):
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi_card("Total Patients", f"{patient_count:,}", "#58a6ff",
                          "In Dataset", "👥"), unsafe_allow_html=True)
    c2.markdown(kpi_card("Elevated Risk (Predicted)", f"{elevated_count}", "#f85149",
                          f"{elevated_count / patient_count * 100:.1f}% of patients", "⚠️"),
                unsafe_allow_html=True)
    c3.markdown(kpi_card("Historical Mortality Rate (DEATH_EVENT = 1)",
                          f"{observed_mortality:.2f}%", "#e3b341",
                          f"{int(observed_count)} of {patient_count} patients", "💛"),
                unsafe_allow_html=True)
    c4.markdown(kpi_card("Model Accuracy", f"{accuracy_val:.2f}%", "#3fb950",
                          "On Cross-Validation", "🎯"), unsafe_allow_html=True)


def _render_performance_strip(accuracy_val, precision_val, recall_val, f1_val, roc_val):
    st.markdown('<span style="color:#e6edf3;font-size:1.05rem;font-weight:600;">'
                'Model Performance (Cross-Validation)</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    perf_defs = [
        ("✅", "Accuracy",             f"{accuracy_val:.2f}%",  "#58a6ff", "Overall correctness"),
        ("🎯", "Precision",            f"{precision_val:.2f}%", "#3fb950", "Correct positive predictions"),
        ("🔁", "Recall (Sensitivity)", f"{recall_val:.2f}%",    "#e3b341", "Actual positives identified"),
        ("🏅", "F1-Score",             f"{f1_val:.2f}%",        "#bc8cff", "Precision × Recall balance"),
        ("📈", "AUC-ROC",              f"{roc_val:.2f}",        "#39d0d8", "Area under ROC curve"),
    ]
    for col, (icon, label, val, color, desc) in zip(st.columns(5), perf_defs):
        col.markdown(f"""
        <div class="section-card" style="text-align:center;padding:1.1rem 0.5rem;">
            <div style="font-size:2.8rem;margin-bottom:0.35rem;">{icon}</div>
            <div style="font-size:0.7rem;font-weight:600;color:#8b949e;text-transform:uppercase;
                 letter-spacing:0.04em;margin-bottom:0.25rem;">{label}</div>
            <div style="font-size:1.6rem;font-weight:700;color:{color};line-height:1.1;">{val}</div>
            <div style="font-size:0.72rem;color:#6e7681;margin-top:0.3rem;">{desc}</div>
            <div style="height:2px;background:{color};border-radius:2px;margin-top:0.6rem;opacity:0.45;"></div>
        </div>""", unsafe_allow_html=True)


def _render_distributions(predictions_df, importance_df, patient_count,
                           elevated_count, survived, observed_count):
    pie_l, pie_r, feat_col = st.columns([1, 1, 1.1])
    low_count = patient_count - elevated_count

    with pie_l:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">Risk Distribution (Predicted)</span>',
                    unsafe_allow_html=True)
        fig1 = go.Figure(go.Pie(
            labels=[f"Elevated Risk ({elevated_count})", f"Low Risk ({low_count})"],
            values=[elevated_count, low_count],
            hole=0.55,
            marker_colors=["#f85149", "#3fb950"],
            textinfo="percent", textfont_size=12,
        ))
        fig1.update_layout(**PLOTLY_LAYOUT,
                           legend=dict(orientation="v", x=0.6, y=0.5,
                                       font_color="#c9d1d9", font_size=11))
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown(info_box("Classified as Elevated or Low Risk based on model-predicted "
                             "probability of adverse outcome."), unsafe_allow_html=True)

    with pie_r:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">'
                    'Historical Outcome Distribution (DEATH_EVENT)</span>',
                    unsafe_allow_html=True)
        fig2 = go.Figure(go.Pie(
            labels=[f"Stable Outcome\n(Survived) ({survived})",
                    f"Adverse Outcome\n(Death) ({int(observed_count)})"],
            values=[survived, int(observed_count)],
            hole=0.55,
            marker_colors=["#3fb950", "#f85149"],
            textinfo="percent", textfont_size=12,
        ))
        fig2.update_layout(**PLOTLY_LAYOUT,
                           legend=dict(orientation="v", x=0.55, y=0.5,
                                       font_color="#c9d1d9", font_size=11))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown(info_box("Distribution reflects actual outcomes observed in the historical dataset."),
                    unsafe_allow_html=True)

    with feat_col:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">'
                    'Top 5 Contributing Risk Factors</span>', unsafe_allow_html=True)
        top5 = importance_df.nlargest(5, 'Importance').sort_values('Importance')
        top5_labels = [FEATURE_LABELS.get(f, f).split(' (')[0] for f in top5['Feature']]
        fig_imp = go.Figure(go.Bar(
            x=top5['Importance'], y=top5_labels, orientation='h',
            marker_color='#7c3aed',
            text=top5['Importance'].round(3),
            textposition='outside',
            textfont=dict(color='#c9d1d9', size=11),
        ))
        fig_imp.update_layout(
            paper_bgcolor="#161b22", plot_bgcolor="#161b22", font_color="#c9d1d9",
            margin=dict(t=10, b=10, l=10, r=50), height=280,
            xaxis=dict(title='Importance Score', gridcolor="#30363d", tickfont_size=11),
            yaxis=dict(gridcolor="#30363d", tickfont_size=11),
            showlegend=False,
        )
        st.plotly_chart(fig_imp, use_container_width=True)
        st.markdown(info_box("Higher importance score indicates greater impact on prediction."),
                    unsafe_allow_html=True)


def _render_key_insights(importance_df, patient_count, elevated_count,
                         observed_mortality, recall_val, roc_val):
    st.markdown('<span style="color:#e6edf3;font-size:1.05rem;font-weight:600;">'
                'Key Insights</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    top2_features = importance_df.nlargest(2, 'Importance')['Feature'].tolist()
    top2_labels   = [FEATURE_LABELS.get(f, f).split(' (')[0] for f in top2_features]

    _KI = ("background:#161b22;border:1px solid #30363d;border-radius:12px;"
           "padding:1.25rem 1rem;text-align:center;height:190px;display:flex;"
           "flex-direction:column;align-items:center;justify-content:center;"
           "gap:0.3rem;box-sizing:border-box;")

    ki1, ki2, ki3, ki4, ki5 = st.columns(5)
    ki1.markdown(f"""<div style="{_KI}">
        <div style="font-size:2rem;line-height:1;flex-shrink:0;">❤️</div>
        <div style="font-size:1.3rem;font-weight:700;color:#e3b341;line-height:1.2;">{observed_mortality:.2f}%</div>
        <div style="font-size:0.78rem;color:#8b949e;line-height:1.45;">Historical mortality rate shows
        the outcome prevalence in the dataset.</div></div>""", unsafe_allow_html=True)

    ki2.markdown(f"""<div style="{_KI}">
        <div style="font-size:2rem;line-height:1;flex-shrink:0;">📈</div>
        <div style="font-size:1.3rem;font-weight:700;color:#e3b341;line-height:1.2;">{recall_val:.2f}%</div>
        <div style="font-size:0.78rem;color:#8b949e;line-height:1.45;">Recall indicates the model
        identifies a majority of high-risk patients.</div></div>""", unsafe_allow_html=True)

    ki3.markdown(f"""<div style="{_KI}">
        <div style="font-size:2rem;line-height:1;flex-shrink:0;">🎯</div>
        <div style="font-size:1.3rem;font-weight:700;color:#39d0d8;line-height:1.2;">{roc_val:.2f}</div>
        <div style="font-size:0.78rem;color:#8b949e;line-height:1.45;">AUC-ROC of {roc_val:.2f}
        indicates moderate discriminatory capability of the model.</div></div>""", unsafe_allow_html=True)

    ki4.markdown(f"""<div style="{_KI}">
        <div style="font-size:2rem;line-height:1;flex-shrink:0;">🔬</div>
        <div style="font-size:0.85rem;font-weight:600;color:#bc8cff;">Top risk drivers</div>
        <div style="font-size:0.78rem;color:#8b949e;line-height:1.45;">{top2_labels[0]} and
        {top2_labels[1]} are the top contributors to elevated risk predictions.</div>
    </div>""", unsafe_allow_html=True)

    ki5.markdown(f"""<div style="{_KI}">
        <div style="font-size:2rem;line-height:1;flex-shrink:0;">⚖️</div>
        <div style="font-size:0.85rem;font-weight:600;color:#e3b341;">Risk vs. Mortality gap</div>
        <div style="font-size:0.78rem;color:#8b949e;line-height:1.45;">
        Predicted elevated-risk rate ({elevated_count / patient_count * 100:.1f}%) is higher than
        the observed mortality rate, reflecting conservative risk flagging.</div>
    </div>""", unsafe_allow_html=True)



# ── Public entry point ─────────────────────────────────────────────────────────

def render() -> None:
    render_page_header(
        "Overview Dashboard",
        "Summary of dataset, model predictions, and historical outcome patterns.",
    )

    predictions_df = pd.read_csv(PREDICTIONS_PATH)
    metrics_df_raw = pd.read_csv(METRICS_PATH)
    importance_df  = pd.read_csv(IMPORTANCE_PATH)

    accuracy_val  = _metric(metrics_df_raw, 'Accuracy')  * 100
    precision_val = _metric(metrics_df_raw, 'Precision') * 100
    recall_val    = _metric(metrics_df_raw, 'Recall')    * 100
    f1_val        = _metric(metrics_df_raw, 'F1 Score')  * 100
    roc_val       = _metric(metrics_df_raw, 'ROC-AUC')

    patient_count      = len(predictions_df)
    elevated_count     = int((predictions_df['probability'] >= RISK_THRESHOLDS['MEDIUM']).sum())
    observed_mortality = predictions_df['DEATH_EVENT'].mean() * 100
    observed_count     = predictions_df['DEATH_EVENT'].sum()
    survived           = patient_count - int(observed_count)

    _render_kpi_row(predictions_df, accuracy_val, patient_count,
                    elevated_count, observed_mortality, observed_count)
    st.markdown("<br>", unsafe_allow_html=True)

    _render_performance_strip(accuracy_val, precision_val, recall_val, f1_val, roc_val)
    st.markdown("<br>", unsafe_allow_html=True)

    _render_distributions(predictions_df, importance_df, patient_count,
                          elevated_count, survived, observed_count)
    st.markdown("<br>", unsafe_allow_html=True)

    _render_key_insights(importance_df, patient_count, elevated_count,
                         observed_mortality, recall_val, roc_val)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(info_box("This dashboard provides an overview of model predictions and historical "
                         "data analysis for educational and research purposes only."),
                unsafe_allow_html=True)

    render_footer()