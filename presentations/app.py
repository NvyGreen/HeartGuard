import os
import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
import pickle

st.set_page_config(
    page_title="Heart Failure Risk Stratification",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0d1117 !important;
    color: #c9d1d9 !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem 2rem !important; }

[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #30363d !important;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
[data-testid="stSidebar"] .stSelectbox label { display: none; }
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }

[data-testid="stSelectbox"] > div > div {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    color: #c9d1d9 !important;
    border-radius: 8px !important;
}

[data-testid="stNumberInput"] input {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    color: #c9d1d9 !important;
    border-radius: 8px !important;
}

.stButton > button {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    color: #c9d1d9 !important;
    border-radius: 8px !important;
}
.stButton > button[kind="primary"] {
    background: #1f6feb !important;
    border-color: #1f6feb !important;
    color: #ffffff !important;
}
.stButton > button:hover {
    border-color: #58a6ff !important;
}

[data-testid="stDataFrame"] {
    background: #161b22 !important;
}

hr { border-color: #30363d !important; }

.page-header {
    border-bottom: 1px solid #30363d;
    padding: 1.5rem 0 1rem 0;
    margin-bottom: 1.5rem;
}
.page-header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #e6edf3;
    margin: 0 0 0.25rem 0;
}
.page-header p {
    color: #8b949e;
    margin: 0;
    font-size: 0.9rem;
}
/* FIX 1: Compact date box */
.page-date {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 0.35rem 0.75rem;
    text-align: right;
    font-size: 0.8rem;
    color: #8b949e;
    white-space: nowrap;
    display: inline-block;
}

.kpi-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    height: 160px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.kpi-card .kpi-label {
    font-size: 0.8rem;
    font-weight: 500;
    color: #8b949e;
    margin-bottom: 0.35rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.kpi-card .kpi-value {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: 0.25rem;
}
.kpi-card .kpi-sub {
    font-size: 0.78rem;
    color: #6e7681;
}
.kpi-card .kpi-bar {
    height: 3px;
    border-radius: 2px;
    margin-top: 0.75rem;
    width: 100%;
}

.section-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.5rem;
}

.info-pill {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 0.75rem 1rem;
}
.info-pill .pill-label {
    font-size: 0.7rem;
    color: #8b949e;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.info-pill .pill-value {
    font-size: 1rem;
    font-weight: 600;
    color: #e6edf3;
    margin-top: 0.25rem;
}

.styled-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.styled-table th {
    background: #21262d;
    padding: 0.6rem 1rem;
    text-align: left;
    font-weight: 600;
    color: #8b949e;
    border-bottom: 1px solid #30363d;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.styled-table td {
    padding: 0.65rem 1rem;
    border-bottom: 1px solid #21262d;
    color: #c9d1d9;
}
.styled-table tr:last-child td { border-bottom: none; }
.styled-table tr:hover td { background: #21262d; }

.info-box {
    background: #0d1b2a;
    border: 1px solid #1f6feb;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.82rem;
    color: #58a6ff;
    display: flex;
    gap: 0.5rem;
    align-items: flex-start;
}

.factor-row {
    display: flex;
    align-items: center;
    margin-bottom: 0.6rem;
    gap: 0.75rem;
    font-size: 0.85rem;
}
.factor-label { width: 160px; color: #c9d1d9; font-weight: 500; flex-shrink: 0; }
.factor-bar-bg { flex: 1; background: #21262d; border-radius: 4px; height: 10px; }
.factor-pct { width: 40px; text-align: right; color: #8b949e; font-size: 0.8rem; }

.disclaimer-box {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 1rem;
    margin-top: 1rem;
}

.footer {
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #30363d;
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #6e7681;
}

/* Make all kpi-card siblings in a row the same height */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] .kpi-card {
    height: 160px !important;
}
</style>
""", unsafe_allow_html=True)

BASE_DIR          = os.path.dirname(os.path.abspath(__file__))
METRICS_PATH      = os.path.join(BASE_DIR, '..', 'notebooks', 'metrics.csv')
IMPORTANCE_PATH   = os.path.join(BASE_DIR, '..', 'notebooks', 'feature_importance.csv')
PREDICTIONS_PATH  = os.path.join(BASE_DIR, '..', 'notebooks', 'predictions.csv')
PIPELINE_PATH     = os.path.join(BASE_DIR, '..', 'notebooks', 'pipeline.pkl')
DATA_PATH         = os.path.join(BASE_DIR, '..', 'data', 'heart_failure_clinical_records_dataset.csv')

RISK_THRESHOLDS = { "HIGH": 0.7, "MEDIUM": 0.4 }
RISK_COLORS     = { "HIGH": "#f85149", "MEDIUM": "#e3b341", "LOW": "#3fb950" }
RISK_LABELS     = { "HIGH": "High Risk", "MEDIUM": "Medium Risk", "LOW": "Low Risk" }

FEATURES = [
    'age', 'anaemia', 'creatinine_phosphokinase', 'diabetes',
    'ejection_fraction', 'high_blood_pressure', 'platelets',
    'serum_creatinine', 'serum_sodium', 'sex', 'smoking'
]
FEATURE_LABELS = {
    'age':                      'Age (years)',
    'anaemia':                  'Anaemia',
    'creatinine_phosphokinase': 'Creatinine Phosphokinase (U/L)',
    'diabetes':                 'Diabetes',
    'ejection_fraction':        'Ejection Fraction (%)',
    'high_blood_pressure':      'High Blood Pressure',
    'platelets':                'Platelets (kiloplatelets/mL)',
    'serum_creatinine':         'Serum Creatinine (mg/dL)',
    'serum_sodium':             'Serum Sodium (mEq/L)',
    'sex':                      'Sex',
    'smoking':                  'Smoking',
}
BOOLEAN_FEATURES = {'anaemia', 'diabetes', 'high_blood_pressure', 'smoking'}

TODAY = date.today().strftime("%b %d, %Y")

def get_risk_category(prob):
    if prob >= RISK_THRESHOLDS['HIGH']:
        return {"category": "HIGH", "label": "High Risk", "color": RISK_COLORS['HIGH']}
    elif prob >= RISK_THRESHOLDS['MEDIUM']:
        return {"category": "MEDIUM", "label": "Medium Risk", "color": RISK_COLORS['MEDIUM']}
    else:
        return {"category": "LOW", "label": "Low Risk", "color": RISK_COLORS['LOW']}

def kpi_card(label, value, color, sub="", icon=""):
    return f"""
    <div class="kpi-card">
        <div style="display:flex;align-items:center;gap:0.5rem;">
            <span style="font-size:1.8rem;line-height:1;flex-shrink:0;">{icon}</span>
            <span class="kpi-label" style="margin:0;font-size:0.72rem;">{label}</span>
        </div>
        <div>
            <div class="kpi-value" style="color:{color};font-size:1.9rem;">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        <div class="kpi-bar" style="background:{color};opacity:0.4;"></div>
    </div>"""

def page_header(title, subtitle):
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.markdown(f"""
        <div class="page-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>""", unsafe_allow_html=True)
    with col_b:
        # FIX 1: compact single-line date box
        st.markdown(f"""
        <div style="margin-top:1.5rem;text-align:right;">
            <span class="page-date">📅 {TODAY}</span>
        </div>""", unsafe_allow_html=True)

def get_risk_flags(patient_dict):
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

    if not flags:
        return [], importance_map
    ranked = sorted(flags.items(), key=lambda x: importance_map.get(x[0], 0), reverse=True)
    return ranked, importance_map

def factor_bars(ranked, importance_map):
    total = sum(importance_map.get(f, 0) for f, _ in ranked) or 1
    html = ""
    colors = ["#f85149", "#e3b341", "#d29922", "#3fb950", "#58a6ff"]
    for i, (feature, _) in enumerate(ranked[:5]):
        imp   = importance_map.get(feature, 0)
        pct   = round(imp / total * 100)
        color = colors[min(i, len(colors)-1)]
        label = FEATURE_LABELS.get(feature, feature).split(' (')[0]
        html += f"""
        <div class="factor-row">
            <div class="factor-label">{label}</div>
            <div class="factor-bar-bg">
                <div style="width:{pct}%;background:{color};height:10px;border-radius:4px;"></div>
            </div>
            <div class="factor-pct">{pct}%</div>
        </div>"""
    return html

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.25rem 1rem 1rem 1rem; border-bottom: 1px solid #30363d; margin-bottom: 1rem;">
        <div style="display:flex; align-items:center; gap:0.75rem;">
            <div style="background:#1a0808; border:2px solid #f85149; border-radius:14px;
                        width:52px; height:52px; display:flex; align-items:center;
                        justify-content:center; flex-shrink:0;">
                <svg width="36" height="36" viewBox="58 20 50 65" xmlns="http://www.w3.org/2000/svg">
                    <path d="M58 58 C58 48 65 42 72 42 C76 42 80 44 82 48 C84 44 88 42 92 42 C99 42 106 48 106 58 C106 70 82 82 82 82 C82 82 58 70 58 58Z"
                          fill="#f85149" opacity="0.25"/>
                    <path d="M58 58 C58 48 65 42 72 42 C76 42 80 44 82 48 C84 44 88 42 92 42 C99 42 106 48 106 58 C106 70 82 82 82 82 C82 82 58 70 58 58Z"
                          fill="none" stroke="#f85149" stroke-width="1.8" stroke-linejoin="round"/>
                    <polyline points="58,60 66,60 70,52 74,68 78,56 82,60 90,60 94,54 98,60 106,60"
                              fill="none" stroke="#f85149" stroke-width="2"
                              stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <div>
                <div style="font-weight:800; font-size:1.1rem; color:#ffffff; letter-spacing:-0.02em;">
                    Heart<span class="logo-guard">Guard</span>
                </div>
                <div style="font-size:0.68rem; color:#8b949e; line-height:1.5; margin-top:2px;">
                    AI-Powered Heart Failure<br>Risk Intelligence
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    div[data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        text-align: left !important;
        background: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1rem !important;
        color: #8b949e !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        margin-bottom: 2px !important;
        transition: background 0.15s !important;
    }
    div[data-testid="stSidebar"] .stButton > button:hover {
        background: #21262d !important;
        color: #e6edf3 !important;
        border: none !important;
    }
    div[data-testid="stSidebar"] .nav-active .stButton > button {
        background: #21262d !important;
        color: #e6edf3 !important;
        border-left: 3px solid #58a6ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if 'page' not in st.session_state:
        st.session_state.page = "🏠  Overview Dashboard"

    nav_items = [
        ("🏠  Overview Dashboard",   "🏠  Overview Dashboard"),
        ("👤  Patient Review",        "👤  Patient Review"),
        ("📊  Model Performance",     "📊  Model Performance"),
        ("🎯  Feature Importance",    "🎯  Feature Importance"),
        ("🧪  Simulated Assessment",  "🧪  Simulated Assessment"),
        ("ℹ️  About / Project Info",  "ℹ️  About / Project Info"),
    ]

    for label, key in nav_items:
        is_active = st.session_state.page == key
        if is_active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{key}"):
            st.session_state.page = key
            st.rerun()
        if is_active:
            st.markdown('</div>', unsafe_allow_html=True)

    page = st.session_state.page

    st.markdown("""
    <div class="disclaimer-box" style="margin-top:2rem;">
        <div style="display:flex;gap:0.5rem;align-items:center;margin-bottom:0.5rem;">
            <span>🛡️</span>
            <span style="font-weight:600;color:#58a6ff !important;font-size:0.85rem;">Disclaimer</span>
        </div>
        <div style="font-size:0.75rem;color:#8b949e !important;line-height:1.5;">
            This tool is for educational and research purposes only. It should not be used as a substitute for
            professional medical advice, diagnosis, or treatment.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Page: Dashboard ────────────────────────────────────────────────────────────
if "Dashboard" in page:
    page_header(
        "Overview Dashboard",
        "Summary of dataset, model predictions, and historical outcome patterns."
    )

    predictions_df = pd.read_csv(PREDICTIONS_PATH)
    metrics_df_raw = pd.read_csv(METRICS_PATH)
    importance_df  = pd.read_csv(IMPORTANCE_PATH)

    def _m(name):
        row = metrics_df_raw[metrics_df_raw['Metric'] == name]
        return row['Mean'].values[0] if len(row) else 0

    accuracy_val  = _m('Accuracy')  * 100
    precision_val = _m('Precision') * 100
    recall_val    = _m('Recall')    * 100
    f1_val        = _m('F1 Score')  * 100
    roc_val       = _m('ROC-AUC')

    patient_count      = len(predictions_df)
    elevated_count     = (predictions_df['probability'] >= RISK_THRESHOLDS['MEDIUM']).sum()
    observed_mortality = predictions_df['DEATH_EVENT'].mean() * 100
    observed_count     = predictions_df['DEATH_EVENT'].sum()
    low_count          = patient_count - elevated_count
    survived           = patient_count - int(observed_count)

    # ── Row 1: KPI cards ──────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi_card("Total Patients", f"{patient_count:,}", "#58a6ff", "In Dataset", "👥"), unsafe_allow_html=True)
    c2.markdown(kpi_card("Elevated Risk (Predicted)", f"{elevated_count}", "#f85149",
        f"{elevated_count/patient_count*100:.1f}% of patients", "⚠️"), unsafe_allow_html=True)
    c3.markdown(kpi_card("Historical Mortality Rate (DEATH_EVENT = 1)",
        f"{observed_mortality:.2f}%", "#e3b341", f"{int(observed_count)} of {patient_count} patients", "💛"), unsafe_allow_html=True)
    c4.markdown(kpi_card("Model Accuracy", f"{accuracy_val:.2f}%", "#3fb950", "On Cross-Validation", "🎯"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Model performance strip ────────────────────────────────────
    # FIX 2 & 3: All 5 cards have icons; icon size increased to 2rem
    st.markdown('<span style="color:#e6edf3;font-size:1.05rem;font-weight:600;">Model Performance (Cross-Validation)</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    perf_defs = [
        ("✅", "Accuracy",             f"{accuracy_val:.2f}%",  "#58a6ff", "Overall correctness"),
        ("🎯", "Precision",            f"{precision_val:.2f}%", "#3fb950", "Correct positive predictions"),
        ("🔁", "Recall (Sensitivity)", f"{recall_val:.2f}%",    "#e3b341", "Actual positives identified"),
        ("🏅", "F1-Score",             f"{f1_val:.2f}%",        "#bc8cff", "Precision × Recall balance"),
        ("📈", "AUC-ROC",              f"{roc_val:.2f}",        "#39d0d8", "Area under ROC curve"),
    ]
    perf_cols = st.columns(5)
    for col, (icon, label, val, color, desc) in zip(perf_cols, perf_defs):
        col.markdown(f"""
        <div class="section-card" style="text-align:center;padding:1.1rem 0.5rem;">
            <div style="font-size:2rem;margin-bottom:0.35rem;">{icon}</div>
            <div style="font-size:0.7rem;font-weight:600;color:#8b949e;text-transform:uppercase;
                 letter-spacing:0.04em;margin-bottom:0.25rem;">{label}</div>
            <div style="font-size:1.6rem;font-weight:700;color:{color};line-height:1.1;">{val}</div>
            <div style="font-size:0.72rem;color:#6e7681;margin-top:0.3rem;">{desc}</div>
            <div style="height:2px;background:{color};border-radius:2px;margin-top:0.6rem;opacity:0.45;"></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    PLOTLY_LAYOUT = dict(
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        font_color="#c9d1d9",
        margin=dict(t=10, b=10, l=10, r=10),
        height=280,
        showlegend=True,
    )

    # ── Row 3: two pie charts + feature importance bar ─────────────────────
    pie_l, pie_r, feat_col = st.columns([1, 1, 1.1])

    with pie_l:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">Risk Distribution (Predicted)</span>', unsafe_allow_html=True)
        fig1 = go.Figure(go.Pie(
            labels=[f"Elevated Risk ({elevated_count})", f"Low Risk ({low_count})"],
            values=[elevated_count, low_count],
            hole=0.55,
            marker_colors=["#f85149", "#3fb950"],
            textinfo="percent",
            textfont_size=12,
        ))
        fig1.update_layout(**PLOTLY_LAYOUT, legend=dict(orientation="v", x=0.6, y=0.5, font_color="#c9d1d9", font_size=11))
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('<div class="info-box">ℹ️ Classified as Elevated or Low Risk based on model-predicted probability of adverse outcome.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with pie_r:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">Historical Outcome Distribution (DEATH_EVENT)</span>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Pie(
            labels=[f"Stable Outcome\n(Survived) ({survived})", f"Adverse Outcome\n(Death) ({int(observed_count)})"],
            values=[survived, int(observed_count)],
            hole=0.55,
            marker_colors=["#3fb950", "#f85149"],
            textinfo="percent",
            textfont_size=12,
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, legend=dict(orientation="v", x=0.55, y=0.5, font_color="#c9d1d9", font_size=11))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('<div class="info-box">ℹ️ Distribution reflects actual outcomes observed in the historical dataset.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with feat_col:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">Top 5 Contributing Risk Factors</span>', unsafe_allow_html=True)
        top5 = importance_df.nlargest(5, 'Importance').sort_values('Importance')
        top5_labels = [FEATURE_LABELS.get(f, f).split(' (')[0] for f in top5['Feature']]
        fig_imp = go.Figure(go.Bar(
            x=top5['Importance'],
            y=top5_labels,
            orientation='h',
            marker_color='#7c3aed',
            text=top5['Importance'].round(3),
            textposition='outside',
            textfont=dict(color='#c9d1d9', size=11),
        ))
        fig_imp.update_layout(
            paper_bgcolor="#161b22", plot_bgcolor="#161b22",
            font_color="#c9d1d9",
            margin=dict(t=10, b=10, l=10, r=50),
            height=280,
            xaxis=dict(title='Importance Score', gridcolor="#30363d", tickfont_size=11),
            yaxis=dict(gridcolor="#30363d", tickfont_size=11),
            showlegend=False,
        )
        st.plotly_chart(fig_imp, use_container_width=True)
        st.markdown('<div class="info-box">ℹ️ Higher importance score indicates greater impact on prediction.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 4: Key Insights ────────────────────────────────────────────────
    st.markdown('<span style="color:#e6edf3;font-size:1.05rem;font-weight:600;">Key Insights</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    top2_features = importance_df.nlargest(2, 'Importance')['Feature'].tolist()
    top2_labels   = [FEATURE_LABELS.get(f, f).split(' (')[0] for f in top2_features]

    ki1, ki2, ki3, ki4, ki5 = st.columns(5)

    # All 5 cards: identical fixed height + flex layout so they never differ
    _KI = "background:#161b22;border:1px solid #30363d;border-radius:12px;padding:1.25rem 1rem;" \
          "text-align:center;height:190px;display:flex;flex-direction:column;" \
          "align-items:center;justify-content:center;gap:0.3rem;box-sizing:border-box;"

    ki1.markdown(f"""
    <div style="{_KI}">
        <div style="font-size:2rem;line-height:1;flex-shrink:0;">❤️</div>
        <div style="font-size:1.3rem;font-weight:700;color:#e3b341;line-height:1.2;">{observed_mortality:.2f}%</div>
        <div style="font-size:0.78rem;color:#8b949e;line-height:1.45;">Historical mortality rate shows the outcome prevalence in the dataset.</div>
    </div>""", unsafe_allow_html=True)

    ki2.markdown(f"""
    <div style="{_KI}">
        <div style="font-size:2rem;line-height:1;flex-shrink:0;">📈</div>
        <div style="font-size:1.3rem;font-weight:700;color:#e3b341;line-height:1.2;">{recall_val:.2f}%</div>
        <div style="font-size:0.78rem;color:#8b949e;line-height:1.45;">Recall indicates the model identifies a majority of high-risk patients.</div>
    </div>""", unsafe_allow_html=True)

    ki3.markdown(f"""
    <div style="{_KI}">
        <div style="font-size:2rem;line-height:1;flex-shrink:0;">🎯</div>
        <div style="font-size:1.3rem;font-weight:700;color:#39d0d8;line-height:1.2;">{roc_val:.2f}</div>
        <div style="font-size:0.78rem;color:#8b949e;line-height:1.45;">AUC-ROC of {roc_val:.2f} indicates moderate discriminatory capability of the model.</div>
    </div>""", unsafe_allow_html=True)

    ki4.markdown(f"""
    <div style="{_KI}">
        <div style="font-size:2rem;line-height:1;flex-shrink:0;">🔬</div>
        <div style="font-size:0.85rem;font-weight:600;color:#bc8cff;">Top risk drivers</div>
        <div style="font-size:0.78rem;color:#8b949e;line-height:1.45;">{top2_labels[0]} and {top2_labels[1]} are the top contributors to elevated risk predictions.</div>
    </div>""", unsafe_allow_html=True)

    ki5.markdown(f"""
    <div style="{_KI}">
        <div style="font-size:2rem;line-height:1;flex-shrink:0;">⚖️</div>
        <div style="font-size:0.85rem;font-weight:600;color:#e3b341;">Risk vs. Mortality gap</div>
        <div style="font-size:0.78rem;color:#8b949e;line-height:1.45;">Predicted elevated-risk rate ({elevated_count/patient_count*100:.1f}%) is higher than the observed mortality rate, reflecting conservative risk flagging.</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 5: Cohort Risk Patterns ────────────────────────────────────────
    st.markdown('<span style="color:#e6edf3;font-size:1.05rem;font-weight:600;">Cohort Risk Patterns</span>', unsafe_allow_html=True)
    st.markdown('<span style="color:#8b949e;font-size:0.85rem;">Mortality and high-risk trends across key clinical indicators.</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    df_full = pd.read_csv(DATA_PATH)
    df_full['probability'] = predictions_df['probability']

    COHORT_PLOTLY = dict(
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        font_color="#c9d1d9",
        margin=dict(t=30, b=30, l=10, r=10),
        height=280,
        xaxis=dict(gridcolor="#30363d"),
        yaxis=dict(gridcolor="#30363d"),
    )

    df_full['ef_band'] = pd.cut(
        df_full['ejection_fraction'],
        bins=[0, 20, 30, 40, 55, 100],
        labels=['≤20%', '21–30%', '31–40%', '41–55%', '>55%']
    )
    ef_df = df_full.groupby('ef_band', observed=True)['DEATH_EVENT'].mean().mul(100).reset_index()
    ef_df.columns = ['EF Band', 'Mortality Rate (%)']

    df_full['sc_band'] = pd.cut(
        df_full['serum_creatinine'],
        bins=[0, 1.2, 2.0, 4.0, 100],
        labels=['≤1.2', '1.2–2.0', '2.0–4.0', '>4.0']
    )
    sc_df = df_full.groupby('sc_band', observed=True)['DEATH_EVENT'].mean().mul(100).reset_index()
    sc_df.columns = ['Creatinine Band', 'Mortality Rate (%)']

    df_full['age_band'] = pd.cut(
        df_full['age'],
        bins=[0, 50, 60, 70, 80, 120],
        labels=['<50', '50–60', '60–70', '70–80', '>80']
    )
    age_df = df_full.groupby('age_band', observed=True)['DEATH_EVENT'].mean().mul(100).reset_index()
    age_df.columns = ['Age Group', 'Mortality Rate (%)']

    row1_col1, row1_col2, row1_col3 = st.columns(3)

    with row1_col1:
        st.markdown('<span style="color:#e6edf3;font-weight:600;font-size:0.9rem;">Mortality Rate by Ejection Fraction</span>', unsafe_allow_html=True)
        fig_ef = px.bar(ef_df, x='EF Band', y='Mortality Rate (%)',
                        color='Mortality Rate (%)',
                        color_continuous_scale=['#3fb950', '#e3b341', '#f85149'])
        fig_ef.update_layout(**COHORT_PLOTLY, coloraxis_showscale=False)
        st.plotly_chart(fig_ef, use_container_width=True)
        st.markdown('<div class="info-box">ℹ️ Lower ejection fraction bands show higher observed mortality rates.</div>', unsafe_allow_html=True)

    with row1_col2:
        st.markdown('<span style="color:#e6edf3;font-weight:600;font-size:0.9rem;">Mortality Rate by Serum Creatinine</span>', unsafe_allow_html=True)
        fig_sc = px.bar(sc_df, x='Creatinine Band', y='Mortality Rate (%)',
                        color='Mortality Rate (%)',
                        color_continuous_scale=['#3fb950', '#e3b341', '#f85149'])
        fig_sc.update_layout(**COHORT_PLOTLY, coloraxis_showscale=False)
        st.plotly_chart(fig_sc, use_container_width=True)
        st.markdown('<div class="info-box">ℹ️ Elevated creatinine is associated with higher observed mortality.</div>', unsafe_allow_html=True)

    with row1_col3:
        st.markdown('<span style="color:#e6edf3;font-weight:600;font-size:0.9rem;">Mortality Rate by Age Group</span>', unsafe_allow_html=True)
        fig_age = px.bar(age_df, x='Age Group', y='Mortality Rate (%)',
                         color='Mortality Rate (%)',
                         color_continuous_scale=['#3fb950', '#e3b341', '#f85149'])
        fig_age.update_layout(**COHORT_PLOTLY, coloraxis_showscale=False)
        st.plotly_chart(fig_age, use_container_width=True)
        st.markdown('<div class="info-box">ℹ️ Mortality rate increases with age across the dataset.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    row2_col1, row2_col2 = st.columns(2)

    conditions = {
        'Diabetes':            'diabetes',
        'High Blood Pressure': 'high_blood_pressure',
        'Anaemia':             'anaemia',
        'Smoking':             'smoking',
    }
    condition_rows = []
    for label, col in conditions.items():
        present = df_full[df_full[col] == 1]
        condition_rows.append({
            'Condition':          label,
            'High Risk Rate (%)': round((present['probability'] >= RISK_THRESHOLDS['HIGH']).mean() * 100, 1),
            'Mortality Rate (%)': round(present['DEATH_EVENT'].mean() * 100, 1),
        })
    cond_df = pd.DataFrame(condition_rows)

    with row2_col1:
        st.markdown('<span style="color:#e6edf3;font-weight:600;font-size:0.9rem;">High Risk Rate by Clinical Condition</span>', unsafe_allow_html=True)
        fig_cond = px.bar(
            cond_df.melt(id_vars='Condition', var_name='Metric', value_name='Rate (%)'),
            x='Condition', y='Rate (%)', color='Metric', barmode='group',
            color_discrete_map={
                'High Risk Rate (%)': '#f85149',
                'Mortality Rate (%)': '#e3b341'
            }
        )
        fig_cond.update_layout(**{**COHORT_PLOTLY, 'height': 300},
                               legend=dict(orientation="h", y=1.1, font_color="#c9d1d9"))
        st.plotly_chart(fig_cond, use_container_width=True)
        st.markdown('<div class="info-box">ℹ️ Patients with these conditions show elevated high-risk and mortality rates.</div>', unsafe_allow_html=True)

    with row2_col2:
        st.markdown('<span style="color:#e6edf3;font-weight:600;font-size:0.9rem;">Predicted Risk Score Distribution</span>', unsafe_allow_html=True)
        fig_hist = px.histogram(
            df_full, x='probability', nbins=20,
            color_discrete_sequence=['#58a6ff'],
        )
        fig_hist.add_vline(x=RISK_THRESHOLDS['MEDIUM'], line_dash='dash',
                           line_color='#e3b341',
                           annotation_text='Medium threshold',
                           annotation_font_color='#e3b341')
        fig_hist.add_vline(x=RISK_THRESHOLDS['HIGH'], line_dash='dash',
                           line_color='#f85149',
                           annotation_text='High threshold',
                           annotation_font_color='#f85149')
        fig_hist.update_layout(**{**COHORT_PLOTLY, 'height': 300},
                               xaxis_title='Predicted Probability',
                               yaxis_title='Patient Count')
        st.plotly_chart(fig_hist, use_container_width=True)
        st.markdown('<div class="info-box">ℹ️ Dashed lines show Medium (0.40) and High (0.70) risk thresholds.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="info-box">ℹ️ This dashboard provides an overview of model predictions and historical data analysis for educational and research purposes only.</div>', unsafe_allow_html=True)

    st.markdown("""<div class="footer">
        <span>❤️ Heart Failure Risk Stratification & Recommendation System &nbsp;|&nbsp; Built with Streamlit, Scikit-learn, Pandas</span>
        <span>For educational and research use only</span>
    </div>""", unsafe_allow_html=True)


# ── Page: Patient Review ───────────────────────────────────────────────────────
elif "Patient Review" in page:
    page_header("Patient Review",
        "Review historical patient cases to understand risk predictions, key indicators, and outcomes.")

    df_full = pd.read_csv(DATA_PATH)
    df_full.insert(0, 'patient_id', [f'P{i:06d}' for i in range(len(df_full))])

    with open(PIPELINE_PATH, 'rb') as f:
        pipeline = pickle.load(f)

    try:
        importance_df  = pd.read_csv(IMPORTANCE_PATH)
        importance_map = dict(zip(importance_df['Feature'], importance_df['Importance']))
    except FileNotFoundError:
        importance_map = {}

    # ── Patient selector row ──────────────────────────────────────────────
    sel_col, info1, info2, info3, info4 = st.columns([2, 1.2, 1.4, 1.6, 1.6])

    with sel_col:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">Select Patient</span>', unsafe_allow_html=True)
        selected_id = st.selectbox("Patient ID", df_full['patient_id'].tolist(),
                                   format_func=lambda x: f"Patient ID: {x}",
                                   label_visibility="collapsed")

    patient_row  = df_full[df_full['patient_id'] == selected_id].iloc[0]
    patient_dict = patient_row[FEATURES].to_dict()
    actual       = int(patient_row['DEATH_EVENT'])
    sex_label    = "Male" if patient_dict['sex'] == 1 else "Female"

    prob          = pipeline.predict_proba(pd.DataFrame([patient_dict])[FEATURES])[0][1]
    risk_category = get_risk_category(prob)
    rc            = risk_category['color']

    outcome_color = "#f85149" if actual == 1 else "#3fb950"
    outcome_text  = "Deceased During Follow-Up" if actual == 1 else "Survived Follow-Up"

    with info1:
        st.markdown(f"""<div class="info-pill">
            <div class="pill-label">👤 Age / Sex</div>
            <div class="pill-value">{int(patient_dict['age'])} / {sex_label}</div>
        </div>""", unsafe_allow_html=True)
    with info2:
        st.markdown(f"""<div class="info-pill">
            <div class="pill-label">📅 Follow-up Time</div>
            <div class="pill-value">{int(patient_row['time'])} days</div>
        </div>""", unsafe_allow_html=True)
    with info3:
        st.markdown(f"""<div class="info-pill">
            <div class="pill-label">❤️ Historical Outcome</div>
            <div class="pill-value" style="color:{outcome_color};font-size:0.9rem;">{outcome_text}</div>
        </div>""", unsafe_allow_html=True)
    with info4:
        st.markdown(f"""<div class="info-pill">
            <div class="pill-label">🛡️ Predicted Risk Level</div>
            <div class="pill-value" style="color:{rc};">{risk_category['label']}</div>
            <div style="font-size:0.72rem;color:#6e7681;">Probability: {prob:.2f} ({prob*100:.0f}%)</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Personalized contributing factors ─────────────────────────────────
    NORMAL_RANGES = {
        'ejection_fraction':        (55,     70,     'low'),
        'serum_creatinine':         (0.7,    1.2,    'high'),
        'serum_sodium':             (135,    145,    'low'),
        'age':                      (0,      60,     'high'),
        'creatinine_phosphokinase': (40,     308,    'high'),
        'platelets':                (150000, 400000, None),
        'diabetes':                 (0,      0,      'high'),
        'high_blood_pressure':      (0,      0,      'high'),
        'anaemia':                  (0,      0,      'high'),
        'smoking':                  (0,      0,      'high'),
        'sex':                      (0,      1,      None),
    }

    def abnormality_score(feature, value):
        if feature not in NORMAL_RANGES:
            return 0
        lo, hi, bad_dir = NORMAL_RANGES[feature]
        if bad_dir == 'high':
            return max(0, (value - hi) / (hi - lo + 1e-9))
        elif bad_dir == 'low':
            return max(0, (lo - value) / (hi - lo + 1e-9))
        else:
            mid = (lo + hi) / 2
            return abs(value - mid) / ((hi - lo) / 2 + 1e-9)

    personalized = {}
    for feature in FEATURES:
        imp    = importance_map.get(feature, 0)
        val    = patient_dict[feature]
        abnorm = abnormality_score(feature, val)
        personalized[feature] = imp * (1 + abnorm)

    total        = sum(personalized.values()) or 1
    top_features = sorted(personalized.items(), key=lambda x: x[1], reverse=True)[:5]

    # ── Main two-column layout ────────────────────────────────────────────
    left_col, right_col = st.columns([1, 1.1])

    with left_col:
        # Patient details table
        rows_html = ""
        for feature, label in FEATURE_LABELS.items():
            val = patient_dict[feature]
            if feature == 'sex':
                display = "Male" if val == 1 else "Female"
            elif feature in BOOLEAN_FEATURES:
                display = "Yes" if val == 1 else "No"
            elif feature == 'platelets':
                display = f"{val/1000:.0f}"
            else:
                display = str(val)
            rows_html += f"<tr><td>{label}</td><td><b style='color:#e6edf3;'>{display}</b></td></tr>"

        st.markdown(f"""
        <div class="section-card">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                <span style="font-size:1rem;">📋</span>
                <span style="font-weight:600;color:#e6edf3;">Patient Details (Clinical Indicators)</span>
            </div>
            <table class="styled-table">
                <thead><tr><th>Indicator</th><th>Value</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            <div class="info-box" style="margin-top:0.75rem;">ℹ️ These values are from the historical dataset.</div>
        </div>""", unsafe_allow_html=True)

        # Contributing factors
        bar_colors = ["#f85149", "#e3b341", "#d29922", "#3fb950", "#58a6ff"]
        factors_html = ""
        for i, (feature, score) in enumerate(top_features):
            pct   = round(score / total * 100)
            color = bar_colors[min(i, len(bar_colors)-1)]
            label = FEATURE_LABELS.get(feature, feature).split(' (')[0]
            factors_html += (
                '<div class="factor-row">'
                f'<div class="factor-label">{label}</div>'
                '<div class="factor-bar-bg">'
                f'<div style="width:{pct}%;background:{color};height:10px;border-radius:4px;"></div>'
                '</div>'
                f'<div class="factor-pct">{pct}%</div>'
                '</div>'
            )

        st.markdown(f"""
        <div style="margin-top:1rem;">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                <span style="font-size:1rem;">🔬</span>
                <span style="font-weight:600;color:#3fb950;">Top Contributing Risk Factors</span>
            </div>
            {factors_html}
            <div style="font-size:0.75rem;color:#6e7681;margin-top:0.25rem;font-style:italic;">
                Percentages indicate relative contribution to the predicted risk.
            </div>
        </div>""", unsafe_allow_html=True)

    with right_col:
        # Risk Assessment panel
        st.markdown(f"""
        <div class="section-card">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">
                <span style="font-size:1rem;">🛡️</span>
                <span style="font-weight:600;color:#e6edf3;">Risk Assessment</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;text-align:center;margin-bottom:1rem;">
                <div>
                    <div style="font-size:0.7rem;font-weight:600;color:#8b949e;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:0.4rem;">Predicted Risk Score</div>
                    <div style="font-size:2.2rem;font-weight:700;color:{rc};line-height:1;">{prob:.2f}</div>
                    <div style="font-size:0.9rem;color:{rc};font-weight:600;">({prob*100:.0f}%)</div>
                    <div style="font-size:0.72rem;color:#6e7681;margin-top:0.4rem;">Probability of adverse outcome<br>(DEATH_EVENT = 1)</div>
                </div>
                <div>
                    <div style="font-size:0.7rem;font-weight:600;color:#8b949e;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:0.4rem;">Risk Category</div>
                    <div style="background:{rc}22;border:1px solid {rc}66;border-radius:8px;padding:0.5rem;margin:0.4rem 0;">
                        <span style="color:{rc};font-weight:700;font-size:0.88rem;">⚠️ {risk_category['label'].upper()}</span>
                    </div>
                    <div style="font-size:0.72rem;color:#6e7681;">Elevated risk of adverse outcome.</div>
                </div>
                <div>
                    <div style="font-size:0.7rem;font-weight:600;color:#8b949e;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:0.4rem;">Interpretation</div>
                    <div style="font-size:0.8rem;color:#c9d1d9;line-height:1.5;margin-top:0.4rem;">
                        The patient's clinical indicators resemble patterns associated with
                        {"elevated" if prob >= RISK_THRESHOLDS["MEDIUM"] else "lower"} adverse outcome
                        risk in the historical dataset.
                    </div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Historical Case Interpretation
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
        key_driver_str = ", ".join(key_drivers[:3]) if key_drivers else "the combined clinical profile"

        comorbidities = []
        if patient_dict['high_blood_pressure'] == 1:
            comorbidities.append("hypertension")
        if patient_dict['diabetes'] == 1:
            comorbidities.append("diabetes")
        if patient_dict['anaemia'] == 1:
            comorbidities.append("anaemia")
        if patient_dict['smoking'] == 1:
            comorbidities.append("smoking history")
        comorbidity_str = " and ".join(comorbidities) if comorbidities else None

        outcome_context = (
            "This patient experienced an adverse outcome during the follow-up period."
            if actual == 1 else
            "This patient survived the follow-up period without an adverse outcome."
        )

        st.markdown(f"""
        <div class="section-card" style="margin-top:1rem;">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                <span style="font-size:1rem;">🔍</span>
                <span style="font-weight:600;color:#e6edf3;">Historical Case Interpretation</span>
            </div>
            <p style="font-size:0.85rem;color:#8b949e;margin:0 0 0.75rem 0;">
                Based on the provided clinical indicators, the model identified patterns commonly
                associated with {"high-risk" if prob >= RISK_THRESHOLDS["HIGH"] else "moderate-risk" if prob >= RISK_THRESHOLDS["MEDIUM"] else "low-risk"} outcomes in similar historical cases.
            </p>
            <div style="display:flex;flex-direction:column;gap:0.6rem;">
                <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                    <div style="background:#f85149;border-radius:50%;width:22px;height:22px;display:flex;
                         align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;">
                        <span style="font-size:0.65rem;font-weight:700;color:#fff;">K</span>
                    </div>
                    <div style="font-size:0.83rem;color:#c9d1d9;line-height:1.5;">
                        <b style="color:#f85149;">Key Driver:</b> {key_driver_str.capitalize()} contributed most to the {"elevated" if prob >= RISK_THRESHOLDS["MEDIUM"] else "predicted"} risk.
                    </div>
                </div>
                {f'''<div style="display:flex;gap:0.75rem;align-items:flex-start;">
                    <div style="background:#e3b341;border-radius:50%;width:22px;height:22px;display:flex;
                         align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;">
                        <span style="font-size:0.65rem;font-weight:700;color:#fff;">C</span>
                    </div>
                    <div style="font-size:0.83rem;color:#c9d1d9;line-height:1.5;">
                        <b style="color:#e3b341;">Comorbidity Impact:</b> History of {comorbidity_str} further {"increases" if prob >= RISK_THRESHOLDS["MEDIUM"] else "contributes to the"} overall risk.
                    </div>
                </div>''' if comorbidity_str else ''}
                <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                    <div style="background:#58a6ff;border-radius:50%;width:22px;height:22px;display:flex;
                         align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;">
                        <span style="font-size:0.65rem;font-weight:700;color:#fff;">O</span>
                    </div>
                    <div style="font-size:0.83rem;color:#c9d1d9;line-height:1.5;">
                        <b style="color:#58a6ff;">Outcome Context:</b> {outcome_context}
                    </div>
                </div>
            </div>
            <p style="font-size:0.75rem;color:#6e7681;margin:0.75rem 0 0 0;font-style:italic;">
                This section provides retrospective interpretation and is <u>not</u> a recommendation for clinical action.
            </p>
        </div>""", unsafe_allow_html=True)

        # Patient Summary (retrospective)
        diab = "diabetes" if patient_dict['diabetes'] == 1 else ""
        hbp  = "hypertension" if patient_dict['high_blood_pressure'] == 1 else ""
        comor = " and ".join(filter(None, [diab, hbp]))
        comor_sent = f" History of {comor} further increased overall risk." if comor else ""

        outcome_sent = (
            "The model predicted high risk of adverse outcome, which was consistent with the observed historical outcome."
            if actual == 1 and prob >= RISK_THRESHOLDS['MEDIUM'] else
            "The model predicted lower risk, and the patient survived the follow-up period."
            if actual == 0 and prob < RISK_THRESHOLDS['MEDIUM'] else
            f"The model predicted {'high' if prob >= RISK_THRESHOLDS['MEDIUM'] else 'low'} risk; the observed outcome was {'adverse' if actual == 1 else 'survival'}."
        )

        st.markdown(f"""
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
                ℹ️ This page is for educational and research purposes only and does not provide clinical advice.
            </div>
        </div>""", unsafe_allow_html=True)


# ── Page: Model Performance ────────────────────────────────────────────────────
elif "Model Performance" in page:
    page_header("Model Performance",
        "Performance evaluation of the Random Forest model using repeated cross-validation.")

    metrics_df = pd.read_csv(METRICS_PATH)
    gap_row    = metrics_df[metrics_df['Metric'] == 'Overfitting Gap']
    metrics_df = metrics_df[metrics_df['Metric'] != 'Overfitting Gap']

    def get_m(name):
        row = metrics_df[metrics_df['Metric'] == name]
        return row.iloc[0] if len(row) else None

    accuracy  = get_m('Accuracy')
    precision = get_m('Precision')
    recall    = get_m('Recall')
    f1        = get_m('F1 Score')
    roc_auc   = get_m('ROC-AUC')

    mc = st.columns(5)
    defs = [
        (accuracy,  "✅", "Accuracy",            "#58a6ff", "Overall correctness"),
        (precision, "🎯", "Precision",            "#3fb950", "Correct positive predictions"),
        (recall,    "🔁", "Recall (Sensitivity)", "#e3b341", "Actual positives identified"),
        (f1,        "🏅", "F1-Score",             "#bc8cff", "Precision × Recall balance"),
        (roc_auc,   "📈", "AUC-ROC",              "#39d0d8", "Area under ROC curve"),
    ]
    for col, (row, icon, label, color, desc) in zip(mc, defs):
        val = f"{row['Mean']*100:.2f}%" if row is not None and label != "AUC-ROC" else (f"{row['Mean']:.2f}" if row is not None else "N/A")
        col.markdown(f"""
        <div class="section-card" style="text-align:center;padding:1.25rem 0.75rem;">
            <div style="font-size:1.5rem;margin-bottom:0.5rem;">{icon}</div>
            <div style="font-size:0.75rem;font-weight:600;color:#8b949e;text-transform:uppercase;letter-spacing:0.04em;">{label}</div>
            <div style="font-size:1.75rem;font-weight:700;color:{color};margin:0.25rem 0;">{val}</div>
            <div style="font-size:0.72rem;color:#6e7681;">{desc}</div>
            <div style="height:3px;background:{color};border-radius:2px;margin-top:0.75rem;opacity:0.5;"></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">Full Cross-Validation Results</span>', unsafe_allow_html=True)
        st.caption("Repeated Stratified K-Fold (5 splits × 10 repeats = 50 evaluations)")
        st.dataframe(metrics_df.set_index('Metric'), use_container_width=True)

        gap = gap_row['Mean'].values[0] if len(gap_row) else 0
        gap_color = "#3fb950" if gap < 0.05 else "#e3b341"
        gap_text  = "Good — model generalises well" if gap < 0.05 else "Potential overfit — monitor closely"
        st.markdown(f"""
        <div style="margin-top:1rem;padding:0.75rem 1rem;background:{gap_color}18;
             border:1px solid {gap_color}44;border-radius:8px;">
            <span style="font-weight:600;color:{gap_color};">Overfitting Gap: {gap:.3f}</span>
            <span style="color:#8b949e;font-size:0.85rem;"> — {gap_text}</span>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">About This Model</span>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box" style="margin:0.75rem 0 1rem 0;">ℹ️ This Random Forest model predicts the likelihood of
            adverse outcome (DEATH_EVENT = 1) based on clinical indicators.
            Evaluation uses repeated stratified cross-validation.</div>
        <table class="styled-table">
            <tbody>
                <tr><td style="color:#8b949e;">Model Type</td><td><b style="color:#e6edf3;">Random Forest Classifier</b></td></tr>
                <tr><td style="color:#8b949e;">Target</td><td><b style="color:#e6edf3;">DEATH_EVENT (1 = Death, 0 = Survived)</b></td></tr>
                <tr><td style="color:#8b949e;">Training Algorithm</td><td><b style="color:#e6edf3;">scikit-learn RandomForestClassifier</b></td></tr>
                <tr><td style="color:#8b949e;">Evaluation</td><td><b style="color:#e6edf3;">Repeated Stratified K-Fold (5×10)</b></td></tr>
                <tr><td style="color:#8b949e;">Class Weighting</td><td><b style="color:#e6edf3;">Balanced</b></td></tr>
                <tr><td style="color:#8b949e;">Max Depth</td><td><b style="color:#e6edf3;">3</b></td></tr>
                <tr><td style="color:#8b949e;">Min Samples Leaf</td><td><b style="color:#e6edf3;">15</b></td></tr>
                <tr><td style="color:#8b949e;">Trained On</td><td><b style="color:#e6edf3;">299 patients</b></td></tr>
            </tbody>
        </table>
        <div style="margin-top:1rem;padding:0.75rem 1rem;background:#12261e;border:1px solid #3fb95044;border-radius:8px;">
            <span style="color:#3fb950;font-weight:600;">✅ Model Status</span><br>
            <span style="font-size:0.82rem;color:#c9d1d9;">Model performance is consistent and acceptable for
            risk stratification and decision support purposes.</span>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<p style="font-size:0.75rem;color:#6e7681;margin-top:1rem;">Note: Metrics are computed via cross-validation and may vary with different random seeds.</p>', unsafe_allow_html=True)


# ── Page: Feature Importance ───────────────────────────────────────────────────
elif "Feature Importance" in page:

    page_header("Feature Importance",
        "Top clinical indicators that contribute most to the model's prediction of adverse outcome.")

    importance_df = pd.read_csv(IMPORTANCE_PATH)

    st.markdown("""
    <div class="info-box" style="margin-bottom:1.5rem;">
        <b>ℹ️ Interpretation Guide:</b> Importance is derived from Gini impurity reduction across all decision trees.
        Higher values indicate stronger influence on the prediction. These represent statistical associations, not clinical causation.
    </div>""", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">Feature Importance (Top 10)</span>', unsafe_allow_html=True)
        fig = px.bar(
            importance_df.sort_values('Importance'),
            x='Importance', y='Feature', orientation='h',
            color='Importance',
            color_continuous_scale=['#3fb950', '#e3b341', '#f85149'],
        )
        fig.update_layout(
            coloraxis_showscale=False, yaxis_title=None,
            xaxis_title='Gini Importance',
            margin=dict(t=10, b=10, l=10, r=10),
            height=380,
            paper_bgcolor="#161b22", plot_bgcolor="#161b22",
            font_color="#c9d1d9",
            xaxis=dict(gridcolor="#30363d"),
            yaxis=dict(gridcolor="#30363d"),
        )
        fig.update_traces(text=importance_df.sort_values('Importance')['Importance'].round(2),
                         textposition='outside', textfont_color="#c9d1d9")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">Full Importance Table</span>', unsafe_allow_html=True)
        display_df = importance_df[['Feature', 'Importance']].copy()
        display_df['Importance'] = display_df['Importance'].round(4)
        st.dataframe(display_df.set_index('Feature'), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    top3 = importance_df.head(3)['Feature'].tolist()
    top3_labels = [FEATURE_LABELS.get(f, f).split(' (')[0] for f in top3]

    with b1:
        st.markdown(f"""<div class="section-card">
            <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                <span style="font-size:1.25rem;">💡</span>
                <div>
                    <div style="font-weight:600;margin-bottom:0.5rem;color:#e6edf3;">Key Takeaway</div>
                    <div style="font-size:0.85rem;color:#c9d1d9;line-height:1.6;">
                        <b style="color:#e6edf3;">{', '.join(top3_labels)}</b> are the most influential indicators in predicting adverse outcomes.
                        These features were most frequently used by decision trees to separate high-risk from low-risk patients.
                    </div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    with b2:
        st.markdown("""<div class="section-card" style="background:#1c1a10;border-color:#e3b34133;">
            <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                <span style="font-size:1.25rem;">📋</span>
                <div>
                    <div style="font-weight:600;margin-bottom:0.5rem;color:#e3b341;">Notes</div>
                    <ul style="font-size:0.82rem;color:#c9d1d9;line-height:1.8;margin:0;padding-left:1.25rem;">
                        <li>Importance values are based on Gini impurity reduction.</li>
                        <li>Higher importance = more frequently used to split data.</li>
                        <li>This model is intended for decision support and educational purposes only.</li>
                    </ul>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)


# ── Page: Simulated Assessment ─────────────────────────────────────────────────
elif "Simulated" in page:
    page_header("Simulated Patient Assessment",
        "Enter patient clinical indicators to estimate risk and receive recommendation.")

    with open(PIPELINE_PATH, 'rb') as f:
        pipeline = pickle.load(f)

    try:
        importance_df  = pd.read_csv(IMPORTANCE_PATH)
        importance_map = dict(zip(importance_df['Feature'], importance_df['Importance']))
    except FileNotFoundError:
        importance_map = {}

    col_form, col_risk, col_rec = st.columns([1, 1, 1])

    with col_form:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">1. Enter Patient Indicators</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        age     = st.number_input("👤 Age (years)",               min_value=1,   max_value=120, value=65)
        anaemia = st.selectbox("🩸 Anaemia",                      ["No", "Yes"])
        diabetes = st.selectbox("🩸 Diabetes",                    ["No", "Yes"])
        ef      = st.number_input("❤️ Ejection Fraction (%)",    min_value=1,   max_value=100, value=38)
        sc      = st.number_input("🩺 Serum Creatinine (mg/dL)", min_value=0.1, max_value=20.0, value=1.1, step=0.1)
        sn      = st.number_input("💧 Serum Sodium (mEq/L)",     min_value=100, max_value=160, value=136)
        hbp     = st.selectbox("❤️ High Blood Pressure",          ["No", "Yes"])
        smoking = st.selectbox("🚬 Smoking",                      ["No", "Yes"])
        platelets = st.number_input("🔬 Platelets (kiloplatelets/mL)", min_value=1, max_value=1000, value=250)
        cpk     = st.number_input("⚙️ Creatinine Phosphokinase (U/L)", min_value=1, max_value=10000, value=200)
        sex     = st.selectbox("⚧ Sex",                           ["Female", "Male"])

        st.markdown('<div class="info-box" style="margin-top:1rem;">ℹ️ Inputs are for demonstration only and are not saved.</div>', unsafe_allow_html=True)

        col_r, col_p = st.columns(2)
        col_r.button("↺ Reset")
        col_p.button("Predict Risk →", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    patient_sim = {
        'age': float(age), 'anaemia': 1 if anaemia == "Yes" else 0,
        'creatinine_phosphokinase': int(cpk),
        'diabetes': 1 if diabetes == "Yes" else 0,
        'ejection_fraction': int(ef), 'high_blood_pressure': 1 if hbp == "Yes" else 0,
        'platelets': float(platelets * 1000),
        'serum_creatinine': float(sc), 'serum_sodium': int(sn),
        'sex': 1 if sex == "Male" else 0,
        'smoking': 1 if smoking == "Yes" else 0,
    }

    prob          = pipeline.predict_proba(pd.DataFrame([patient_sim])[FEATURES])[0][1]
    risk_category = get_risk_category(prob)
    ranked, _     = get_risk_flags(patient_sim)
    rc = risk_category['color']

    with col_risk:
        NORMAL_RANGES = {
            'ejection_fraction':        (55,     70,     'low'),
            'serum_creatinine':         (0.7,    1.2,    'high'),
            'serum_sodium':             (135,    145,    'low'),
            'age':                      (0,      60,     'high'),
            'creatinine_phosphokinase': (40,     308,    'high'),
            'platelets':                (150000, 400000, None),
            'diabetes':                 (0,      0,      'high'),
            'high_blood_pressure':      (0,      0,      'high'),
            'anaemia':                  (0,      0,      'high'),
            'smoking':                  (0,      0,      'high'),
            'sex':                      (0,      1,      None),
        }

        def abnormality_score(feature, value):
            if feature not in NORMAL_RANGES:
                return 0
            lo, hi, bad_dir = NORMAL_RANGES[feature]
            if bad_dir == 'high':
                return max(0, (value - hi) / (hi - lo + 1e-9))
            elif bad_dir == 'low':
                return max(0, (lo - value) / (hi - lo + 1e-9))
            else:
                mid = (lo + hi) / 2
                return abs(value - mid) / ((hi - lo) / 2 + 1e-9)

        personalized = {}
        for feature in FEATURES:
            imp    = importance_map.get(feature, 0)
            val    = patient_sim[feature]
            abnorm = abnormality_score(feature, val)
            personalized[feature] = imp * (1 + abnorm)

        total = sum(personalized.values()) or 1
        top_features = sorted(personalized.items(), key=lambda x: x[1], reverse=True)[:5]

        bar_colors = ["#f85149", "#e3b341", "#d29922", "#3fb950", "#58a6ff"]
        top_factors_html = ""
        for i, (feature, score) in enumerate(top_features):
            pct   = round(score / total * 100)
            color = bar_colors[min(i, len(bar_colors)-1)]
            label = FEATURE_LABELS.get(feature, feature).split(' (')[0]
            top_factors_html += (
                '<div class="factor-row">'
                f'<div class="factor-label">{label}</div>'
                '<div class="factor-bar-bg">'
                f'<div style="width:{pct}%;background:{color};height:10px;border-radius:4px;"></div>'
                '</div>'
                f'<div class="factor-pct">{pct}%</div>'
                '</div>'
            )
        top_factors_html += '<div style="font-size:0.75rem;color:#6e7681;margin-top:0.25rem;">Based on model importance \xd7 how abnormal this patient\'s values are.</div>'

        factors_section = (
            "<div style='margin-top:1rem;'>"
            "<span style='color:#e6edf3;font-weight:600;font-size:0.9rem;'>Top Contributing Factors</span>"
            "<div style='margin-top:0.5rem;'>" + top_factors_html + "</div>"
            "</div>"
        )

        st.markdown(f"""
        <div class="section-card">
            <span style="color:#e6edf3;font-weight:600;">2. Risk Assessment</span>
            <div style="text-align:center;padding:1.5rem 0 1rem 0;">
                <div style="font-size:3rem;font-weight:700;color:{rc};line-height:1;">{prob:.2f}</div>
                <div style="font-size:1.25rem;font-weight:600;color:{rc};">{prob*100:.0f}%</div>
                <div style="font-size:0.8rem;color:#6e7681;margin-top:0.5rem;">
                    Higher score = higher risk of adverse outcome.
                </div>
            </div>
            <div style="background:{rc}18;border:1px solid {rc}44;border-radius:8px;
                 padding:0.75rem;text-align:center;margin-bottom:1rem;">
                <span style="color:{rc};font-weight:700;font-size:1.1rem;">
                    \u26a0\ufe0f {risk_category['label'].upper()}
                </span>
            </div>
            <div class="info-box">\u2139\ufe0f This profile matches historical patients with {"elevated" if prob >= RISK_THRESHOLDS["MEDIUM"] else "lower"} short-term adverse outcomes.</div>
            {factors_section}
        </div>""", unsafe_allow_html=True)

        explanation_lines = []

        ef_val = patient_sim['ejection_fraction']
        if ef_val < 40:
            explanation_lines.append(
                f"Low ejection fraction ({ef_val}%) — heart is pumping less than 40% of blood per beat, "
                "indicating reduced cardiac output."
            )
        elif ef_val < 55:
            explanation_lines.append(
                f"Mildly reduced ejection fraction ({ef_val}%) — below the normal range of 55–70%."
            )

        sc_val = patient_sim['serum_creatinine']
        if sc_val > 2.0:
            explanation_lines.append(
                f"Elevated serum creatinine ({sc_val} mg/dL) — above the normal range (0.7–1.2 mg/dL), "
                "suggesting reduced kidney function."
            )
        elif sc_val > 1.2:
            explanation_lines.append(
                f"Borderline serum creatinine ({sc_val} mg/dL) — slightly above normal, "
                "which may reflect early renal stress."
            )

        sn_val = patient_sim['serum_sodium']
        if sn_val < 130:
            explanation_lines.append(
                f"Critically low serum sodium ({sn_val} mEq/L) — severe hyponatremia strongly "
                "associated with poor cardiac outcomes."
            )
        elif sn_val < 135:
            explanation_lines.append(
                f"Low serum sodium ({sn_val} mEq/L) — below normal (135–145 mEq/L), "
                "which is linked to worse heart failure prognosis."
            )

        age_val = int(patient_sim['age'])
        if age_val > 70:
            explanation_lines.append(
                f"Advanced age ({age_val} years) — patients over 70 show higher rates of "
                "adverse outcomes in this dataset."
            )

        if patient_sim['diabetes'] == 1:
            explanation_lines.append(
                "Diabetes present — associated with accelerated cardiovascular disease and "
                "worse heart failure outcomes."
            )
        if patient_sim['high_blood_pressure'] == 1:
            explanation_lines.append(
                "High blood pressure — increases cardiac workload and is linked to "
                "higher risk of adverse events."
            )
        if patient_sim['anaemia'] == 1:
            explanation_lines.append(
                "Anaemia present — reduces oxygen-carrying capacity, placing additional "
                "strain on the heart."
            )
        if patient_sim['smoking'] == 1:
            explanation_lines.append(
                "Smoking — associated with accelerated arterial damage and reduced "
                "cardiac reserve."
            )

        cpk_val = patient_sim['creatinine_phosphokinase']
        if cpk_val > 1000:
            explanation_lines.append(
                f"Elevated CPK ({cpk_val} U/L) — significantly above normal range, "
                "may indicate myocardial or skeletal muscle stress."
            )

        if not explanation_lines:
            explanation_lines.append(
                "No individual clinical values are outside normal ranges. "
                "The model's prediction is based on the combined profile of all indicators."
            )

        bullets_exp  = "".join(
            f"<li style='margin-bottom:0.5rem;font-size:0.83rem;color:#c9d1d9;line-height:1.5;'>{line}</li>"
            for line in explanation_lines
        )

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
            <ul style="margin:0;padding-left:1.25rem;">
                {bullets_exp}
            </ul>
            <p style="font-size:0.78rem;color:#6e7681;margin:0.75rem 0 0 0;font-style:italic;">
                These factors have been associated with {"higher" if prob >= RISK_THRESHOLDS["MEDIUM"] else "lower"} rates of adverse outcomes
                in similar historical patients.
            </p>
        </div>""", unsafe_allow_html=True)

    with col_rec:
        st.markdown('<span style="color:#e6edf3;font-weight:600;">3. Recommendation</span>', unsafe_allow_html=True)
        cat = risk_category['category']

        if cat == "HIGH":
            bullets = ["Consider closer monitoring and follow-up.",
                       "Review and optimize heart failure management.",
                       "Evaluate need for specialist or advanced care consultation.",
                       "Patient may benefit from early intervention strategies."]
        elif cat == "MEDIUM":
            bullets = ["Schedule follow-up within 7 days.",
                       "Monitor serum creatinine and ejection fraction closely.",
                       "Consider cardiology referral if symptoms worsen."]
        else:
            bullets = ["Continue routine monitoring.",
                       "Reassess if symptoms worsen or new risk factors emerge.",
                       "Maintain current management plan."]

        bullets_html = "".join(f"<li style='margin-bottom:0.4rem;font-size:0.85rem;color:#c9d1d9;'>{b}</li>" for b in bullets)
        st.markdown(f"""
        <div style="background:{rc}18;border:1px solid {rc}44;border-radius:8px;padding:1rem;margin:0.75rem 0;">
            <div style="font-weight:600;color:{rc};margin-bottom:0.5rem;">⚠️ Recommended Action</div>
            <p style="font-size:0.85rem;margin:0 0 0.5rem 0;color:#c9d1d9;">Patient is at
                <b style="color:{rc};">{risk_category['label'].upper()}</b>.</p>
            <ul style="margin:0;padding-left:1.25rem;">{bullets_html}</ul>
        </div>

        <div style="background:#1c1a10;border:1px solid #e3b34133;border-radius:8px;padding:1rem;margin-bottom:0.75rem;">
            <div style="font-weight:600;color:#e3b341;margin-bottom:0.4rem;">💡 Why This Recommendation?</div>
            <div style="font-size:0.82rem;color:#c9d1d9;">Patients with similar clinical indicators in the historical
                dataset had a {"higher" if prob >= RISK_THRESHOLDS["MEDIUM"] else "lower"} rate of adverse outcomes
                within the observed follow-up period.</div>
        </div>

        <div style="background:#12261e;border:1px solid #3fb95033;border-radius:8px;padding:1rem;margin-bottom:0.75rem;">
            <div style="font-weight:600;color:#3fb950;margin-bottom:0.4rem;">🛡️ Disclaimer</div>
            <div style="font-size:0.82rem;color:#c9d1d9;">This recommendation is generated by an AI model and is
                intended for decision-support and educational purposes only.
                Not a substitute for clinical judgment.</div>
        </div>

        <div style="background:#21262d;border:1px solid #30363d;border-radius:8px;padding:1rem;">
            <div style="font-weight:600;color:#e6edf3;margin-bottom:0.4rem;">📄 Input Summary</div>
            <div style="font-size:0.8rem;color:#8b949e;line-height:1.7;">
                Age: {age}, EF: {ef}%, Creatinine: {sc}, Sodium: {sn},<br>
                Diabetes: {diabetes}, Anaemia: {anaemia}, BP: {hbp}, Smoking: {smoking},<br>
                Sex: {sex}, Platelets: {platelets}k/mL, CPK: {cpk} U/L
            </div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Page: About ────────────────────────────────────────────────────────────────
elif "About" in page:
    page_header("About / Project Info",
        "Learn more about the dataset, methodology, AI model, and technology used in this project.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""<div class="section-card">
            <div style="display:flex;gap:0.75rem;align-items:center;margin-bottom:1rem;">
                <div style="background:#0d1b2a;border-radius:8px;padding:0.5rem;font-size:1.25rem;">🗄️</div>
                <b style="color:#e6edf3;">1. Dataset Information</b>
            </div>
            <div style="font-size:0.85rem;color:#8b949e;margin-bottom:1rem;">
                The model is built using the Heart Failure Clinical Records Dataset.
            </div>
            <table class="styled-table">
                <tbody>
                    <tr><td style="color:#8b949e;">Source</td><td><b style="color:#e6edf3;">Kaggle</b></td></tr>
                    <tr><td style="color:#8b949e;">File</td><td><b style="color:#e6edf3;">heart_failure_clinical_records_dataset.csv</b></td></tr>
                    <tr><td style="color:#8b949e;">Total Records</td><td><b style="color:#e6edf3;">299</b></td></tr>
                    <tr><td style="color:#8b949e;">Features</td><td><b style="color:#e6edf3;">11 clinical indicators</b></td></tr>
                    <tr><td style="color:#8b949e;">Target Variable</td><td><b style="color:#e6edf3;">DEATH_EVENT (1 = Death, 0 = Survived)</b></td></tr>
                </tbody>
            </table>
            <div class="info-box" style="margin-top:1rem;">ℹ️ This dataset contains de-identified patient clinical records.</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown("""<div class="section-card">
            <div style="display:flex;gap:0.75rem;align-items:center;margin-bottom:1rem;">
                <div style="background:#12261e;border-radius:8px;padding:0.5rem;font-size:1.25rem;">⚙️</div>
                <b style="color:#e6edf3;">2. Methodology</b>
            </div>
            <div style="font-size:0.85rem;color:#8b949e;margin-bottom:1rem;">
                End-to-end workflow for building this risk stratification system.
            </div>""", unsafe_allow_html=True)
        steps = [
            ("Data Loading & Validation",    "Load and validate the clinical dataset."),
            ("Data Preprocessing",           "Handle missing values, encode variables, prepare features."),
            ("Model Training",               "Train Random Forest on full dataset after cross-validation."),
            ("Model Evaluation",             "Evaluate performance using repeated stratified K-fold."),
            ("Risk Scoring & Categorization","Generate risk probability and categorize into Low / Medium / High."),
            ("Recommendation Engine",        "Provide risk-aware recommendations and explanations."),
        ]
        for i, (title, desc) in enumerate(steps, 1):
            st.markdown(f"""
            <div style="display:flex;gap:0.75rem;margin-bottom:0.75rem;align-items:flex-start;">
                <div style="background:#3fb950;color:#0d1117;border-radius:50%;width:22px;height:22px;
                     display:flex;align-items:center;justify-content:center;font-size:0.72rem;
                     font-weight:700;flex-shrink:0;margin-top:2px;">{i}</div>
                <div><div style="font-weight:600;font-size:0.85rem;color:#e6edf3;">{title}</div>
                <div style="font-size:0.8rem;color:#8b949e;">{desc}</div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown("""<div class="section-card">
            <div style="display:flex;gap:0.75rem;align-items:center;margin-bottom:1rem;">
                <div style="background:#1a1030;border-radius:8px;padding:0.5rem;font-size:1.25rem;">🧠</div>
                <b style="color:#e6edf3;">3. AI Model Details</b>
            </div>
            <table class="styled-table">
                <tbody>
                    <tr><td style="color:#8b949e;">Model</td><td><b style="color:#e6edf3;">Random Forest</b></td></tr>
                    <tr><td style="color:#8b949e;">Type</td><td><b style="color:#e6edf3;">Binary Classification</b></td></tr>
                    <tr><td style="color:#8b949e;">Target</td><td><b style="color:#e6edf3;">DEATH_EVENT (1=Death, 0=Survived)</b></td></tr>
                    <tr><td style="color:#8b949e;">Training</td><td><b style="color:#e6edf3;">scikit-learn RandomForestClassifier</b></td></tr>
                    <tr><td style="color:#8b949e;">Evaluation</td><td><b style="color:#e6edf3;">Accuracy, Precision, Recall, F1, AUC-ROC</b></td></tr>
                    <tr><td style="color:#8b949e;">Feature Importance</td><td><b style="color:#e6edf3;">Gini impurity reduction</b></td></tr>
                    <tr><td style="color:#8b949e;">Class Weighting</td><td><b style="color:#e6edf3;">Balanced</b></td></tr>
                    <tr><td style="color:#8b949e;">Trained On</td><td><b style="color:#e6edf3;">Historical clinical records</b></td></tr>
                </tbody>
            </table>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#1c1a10;border:1px solid #e3b34133;border-radius:10px;padding:1.25rem 1.5rem;margin-bottom:1.5rem;">
        <div style="font-weight:600;color:#e3b341;margin-bottom:0.4rem;">⚠️ Important Disclaimer</div>
        <div style="font-size:0.85rem;color:#c9d1d9;line-height:1.6;">
            This application is intended for educational and research purposes only. It is a decision-support tool
            and not a substitute for professional medical judgment. Always consult qualified healthcare professionals
            for medical advice, diagnosis, and treatment.
        </div>
    </div>""", unsafe_allow_html=True)

    tech_col, how_col = st.columns(2)
    with tech_col:
        st.markdown("""<div class="section-card">
            <div style="display:flex;gap:0.75rem;align-items:center;margin-bottom:1rem;">
                <span style="font-size:1.1rem;">💻</span><b style="color:#e6edf3;">4. Technology Stack</b>
            </div>
            <div style="display:flex;gap:1.5rem;flex-wrap:wrap;font-size:0.82rem;color:#c9d1d9;">
                <div style="text-align:center;"><div style="font-size:1.5rem;">🐍</div><b style="color:#e6edf3;">Python</b><br><span style="color:#6e7681;">3.10+</span></div>
                <div style="text-align:center;"><div style="font-size:1.5rem;">🎈</div><b style="color:#e6edf3;">Streamlit</b><br><span style="color:#6e7681;">1.30+</span></div>
                <div style="text-align:center;"><div style="font-size:1.5rem;">🤖</div><b style="color:#e6edf3;">scikit-learn</b><br><span style="color:#6e7681;">1.4+</span></div>
                <div style="text-align:center;"><div style="font-size:1.5rem;">🐼</div><b style="color:#e6edf3;">pandas</b><br><span style="color:#6e7681;">2.2+</span></div>
                <div style="text-align:center;"><div style="font-size:1.5rem;">🔢</div><b style="color:#e6edf3;">NumPy</b><br><span style="color:#6e7681;">1.26+</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

    with how_col:
        st.markdown("""<div class="section-card">
            <div style="display:flex;gap:0.75rem;align-items:center;margin-bottom:1rem;">
                <span style="font-size:1.1rem;">📖</span><b style="color:#e6edf3;">5. How to Use This App</b>
            </div>
            <div style="font-size:0.85rem;color:#c9d1d9;line-height:1.8;">
                <div>✅ Explore the dashboard for key insights and risk distribution.</div>
                <div>✅ Review individual patient records and model predictions.</div>
                <div>✅ Analyze model performance and feature importance.</div>
                <div>✅ Use the simulated assessment to evaluate patient scenarios.</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="footer">
        <span>❤️ Heart Failure Risk Stratification & Recommendation System &nbsp;|&nbsp; Built with Streamlit, Scikit-learn, Pandas</span>
        <span>© 2025 All rights reserved</span>
    </div>""", unsafe_allow_html=True)