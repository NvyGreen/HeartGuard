import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.constants import (
    DATA_PATH, IMPORTANCE_PATH, METRICS_PATH, PREDICTIONS_PATH,
    FEATURE_LABELS, PLOTLY_LAYOUT, RISK_THRESHOLDS,
)
from utils.ui_components import (
    info_box, kpi_card, render_footer, render_page_header,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _metric(metrics_df: pd.DataFrame, name: str) -> float:
    row = metrics_df[metrics_df['Metric'] == name]
    return float(row['Mean'].values[0]) if len(row) else 0.0


_COHORT_LAYOUT = dict(
    paper_bgcolor="#161b22",
    plot_bgcolor="#161b22",
    font_color="#c9d1d9",
    margin=dict(t=30, b=30, l=10, r=10),
    height=280,
    xaxis=dict(gridcolor="#30363d"),
    yaxis=dict(gridcolor="#30363d"),
)

_GRADIENT = ['#3fb950', '#e3b341', '#f85149']


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
            <div style="font-size:2rem;margin-bottom:0.35rem;">{icon}</div>
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


def _render_cohort_patterns(df_full):
    st.markdown('<span style="color:#e6edf3;font-size:1.05rem;font-weight:600;">'
                'Cohort Risk Patterns</span>', unsafe_allow_html=True)
    st.markdown('<span style="color:#8b949e;font-size:0.85rem;">'
                'Mortality and high-risk trends across key clinical indicators.</span>',
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Band definitions
    df_full['ef_band'] = pd.cut(
        df_full['ejection_fraction'],
        bins=[0, 20, 30, 40, 55, 100],
        labels=['≤20%', '21–30%', '31–40%', '41–55%', '>55%'],
    )
    df_full['sc_band'] = pd.cut(
        df_full['serum_creatinine'],
        bins=[0, 1.2, 2.0, 4.0, 100],
        labels=['≤1.2', '1.2–2.0', '2.0–4.0', '>4.0'],
    )
    df_full['age_band'] = pd.cut(
        df_full['age'],
        bins=[0, 50, 60, 70, 80, 120],
        labels=['<50', '50–60', '60–70', '70–80', '>80'],
    )

    ef_df  = (df_full.groupby('ef_band',  observed=True)['DEATH_EVENT']
                     .mean().mul(100).reset_index()
                     .rename(columns={'ef_band': 'EF Band', 'DEATH_EVENT': 'Mortality Rate (%)'}))
    sc_df  = (df_full.groupby('sc_band',  observed=True)['DEATH_EVENT']
                     .mean().mul(100).reset_index()
                     .rename(columns={'sc_band': 'Creatinine Band', 'DEATH_EVENT': 'Mortality Rate (%)'}))
    age_df = (df_full.groupby('age_band', observed=True)['DEATH_EVENT']
                     .mean().mul(100).reset_index()
                     .rename(columns={'age_band': 'Age Group', 'DEATH_EVENT': 'Mortality Rate (%)'}))

    row1_col1, row1_col2, row1_col3 = st.columns(3)
    charts = [
        (row1_col1, ef_df,  'EF Band',         'Mortality Rate by Ejection Fraction',
         'Lower ejection fraction bands show higher observed mortality rates.'),
        (row1_col2, sc_df,  'Creatinine Band',  'Mortality Rate by Serum Creatinine',
         'Elevated creatinine is associated with higher observed mortality.'),
        (row1_col3, age_df, 'Age Group',        'Mortality Rate by Age Group',
         'Mortality rate increases with age across the dataset.'),
    ]
    for col, data, x_col, title, note in charts:
        with col:
            st.markdown(f'<span style="color:#e6edf3;font-weight:600;font-size:0.9rem;">'
                        f'{title}</span>', unsafe_allow_html=True)
            fig = px.bar(data, x=x_col, y='Mortality Rate (%)',
                         color='Mortality Rate (%)',
                         color_continuous_scale=_GRADIENT)
            fig.update_layout(**_COHORT_LAYOUT, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(info_box(note), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    row2_col1, row2_col2 = st.columns(2)

    # Condition comparison
    conditions = {
        'Diabetes':            'diabetes',
        'High Blood Pressure': 'high_blood_pressure',
        'Anaemia':             'anaemia',
        'Smoking':             'smoking',
    }
    cond_rows = []
    for label, col in conditions.items():
        present = df_full[df_full[col] == 1]
        cond_rows.append({
            'Condition':          label,
            'High Risk Rate (%)': round(
                (present['probability'] >= RISK_THRESHOLDS['HIGH']).mean() * 100, 1
            ),
            'Mortality Rate (%)': round(present['DEATH_EVENT'].mean() * 100, 1),
        })
    cond_df = pd.DataFrame(cond_rows)

    with row2_col1:
        st.markdown('<span style="color:#e6edf3;font-weight:600;font-size:0.9rem;">'
                    'High Risk Rate by Clinical Condition</span>', unsafe_allow_html=True)
        fig_cond = px.bar(
            cond_df.melt(id_vars='Condition', var_name='Metric', value_name='Rate (%)'),
            x='Condition', y='Rate (%)', color='Metric', barmode='group',
            color_discrete_map={
                'High Risk Rate (%)': '#f85149',
                'Mortality Rate (%)': '#e3b341',
            },
        )
        fig_cond.update_layout(**{**_COHORT_LAYOUT, 'height': 300},
                               legend=dict(orientation="h", y=1.1, font_color="#c9d1d9"))
        st.plotly_chart(fig_cond, use_container_width=True)
        st.markdown(info_box("Patients with these conditions show elevated high-risk "
                             "and mortality rates."), unsafe_allow_html=True)

    with row2_col2:
        st.markdown('<span style="color:#e6edf3;font-weight:600;font-size:0.9rem;">'
                    'Predicted Risk Score Distribution</span>', unsafe_allow_html=True)
        fig_hist = px.histogram(df_full, x='probability', nbins=20,
                                color_discrete_sequence=['#58a6ff'])
        fig_hist.add_vline(x=RISK_THRESHOLDS['MEDIUM'], line_dash='dash',
                           line_color='#e3b341', annotation_text='Medium threshold',
                           annotation_font_color='#e3b341')
        fig_hist.add_vline(x=RISK_THRESHOLDS['HIGH'], line_dash='dash',
                           line_color='#f85149', annotation_text='High threshold',
                           annotation_font_color='#f85149')
        fig_hist.update_layout(**{**_COHORT_LAYOUT, 'height': 300},
                               xaxis_title='Predicted Probability',
                               yaxis_title='Patient Count')
        st.plotly_chart(fig_hist, use_container_width=True)
        st.markdown(info_box("Dashed lines show Medium (0.40) and High (0.70) risk thresholds."),
                    unsafe_allow_html=True)


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

    df_full = pd.read_csv(DATA_PATH)
    df_full['probability'] = predictions_df['probability']
    _render_cohort_patterns(df_full)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(info_box("This dashboard provides an overview of model predictions and historical "
                         "data analysis for educational and research purposes only."),
                unsafe_allow_html=True)

    render_footer()