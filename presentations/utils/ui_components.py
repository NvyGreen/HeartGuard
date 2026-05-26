import streamlit as st
from utils.constants import TODAY, RISK_COLORS


# ── Global CSS ─────────────────────────────────────────────────────────────────

def inject_global_css() -> None:
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
.stButton > button:hover { border-color: #58a6ff !important; }

[data-testid="stDataFrame"] { background: #161b22 !important; }

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
.page-header p { color: #8b949e; margin: 0; font-size: 0.9rem; }

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
.kpi-card .kpi-sub { font-size: 0.78rem; color: #6e7681; }
.kpi-card .kpi-bar { height: 3px; border-radius: 2px; margin-top: 0.75rem; width: 100%; }

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

div[data-testid="stHorizontalBlock"] > div[data-testid="column"] .kpi-card {
    height: 160px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Page-level widgets ─────────────────────────────────────────────────────────

def render_page_header(title: str, subtitle: str) -> None:
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.markdown(f"""
        <div class="page-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div style="margin-top:1.5rem;text-align:right;">
            <span class="page-date">📅 {TODAY}</span>
        </div>""", unsafe_allow_html=True)


def render_footer(right_text: str = "For educational and research use only") -> None:
    st.markdown(f"""<div class="footer">
        <span>❤️ Heart Failure Risk Stratification &amp; Recommendation System
              &nbsp;|&nbsp; Built with Streamlit, Scikit-learn, Pandas</span>
        <span>{right_text}</span>
    </div>""", unsafe_allow_html=True)


def render_disclaimer_sidebar() -> None:
    st.markdown("""
    <div class="disclaimer-box" style="margin-top:2rem;">
        <div style="display:flex;gap:0.5rem;align-items:center;margin-bottom:0.5rem;">
            <span>🛡️</span>
            <span style="font-weight:600;color:#58a6ff !important;font-size:0.85rem;">Disclaimer</span>
        </div>
        <div style="font-size:0.75rem;color:#8b949e !important;line-height:1.5;">
            This tool is for educational and research purposes only. It should not be used as a
            substitute for professional medical advice, diagnosis, or treatment.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Card HTML builders ─────────────────────────────────────────────────────────

def kpi_card(label: str, value: str, color: str, sub: str = "", icon: str = "") -> str:
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


def info_box(text: str) -> str:
    return f'<div class="info-box">ℹ️ {text}</div>'


def section_card(inner_html: str, extra_style: str = "") -> str:
    return f'<div class="section-card" style="{extra_style}">{inner_html}</div>'


def info_pill(label: str, value: str, value_color: str = "#e6edf3",
              sub: str = "") -> str:
    sub_html = (
        f'<div style="font-size:0.72rem;color:#6e7681;margin-top:0.2rem;">{sub}</div>'
        if sub else ""
    )
    return (
        '<div style="background:#21262d;border:1px solid #30363d;border-radius:8px;'
        'padding:0.75rem 1rem;">'
        f'<div style="font-size:0.7rem;color:#8b949e;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.05em;">{label}</div>'
        f'<div style="font-size:1rem;font-weight:600;color:{value_color};'
        f'margin-top:0.25rem;">{value}</div>'
        f'{sub_html}'
        '</div>'
    )


# ── Factor bars ────────────────────────────────────────────────────────────────

BAR_COLORS = ["#f85149", "#e3b341", "#d29922", "#3fb950", "#58a6ff"]


def factor_bars_html(top_features: list, total: float,
                     feature_labels: dict) -> str:
    """Render horizontal factor-importance bars for up to 5 features."""
    html = ""
    for i, (feature, score) in enumerate(top_features[:5]):
        pct   = round(score / total * 100)
        color = BAR_COLORS[min(i, len(BAR_COLORS) - 1)]
        label = feature_labels.get(feature, feature).split(' (')[0]
        html += (
            '<div class="factor-row">'
            f'<div class="factor-label">{label}</div>'
            '<div class="factor-bar-bg">'
            f'<div style="width:{pct}%;background:{color};height:10px;border-radius:4px;"></div>'
            '</div>'
            f'<div class="factor-pct">{pct}%</div>'
            '</div>'
        )
    return html


# ── Sidebar navigation ─────────────────────────────────────────────────────────

SIDEBAR_LOGO_HTML = """
<div style="padding: 1.25rem 1rem 1rem 1rem; border-bottom: 1px solid #30363d; margin-bottom: 1rem;">
    <div style="display:flex; align-items:center; gap:0.75rem;">
        <div style="background:#1a0808; border:2px solid #f85149; border-radius:14px;
                    width:52px; height:52px; display:flex; align-items:center;
                    justify-content:center; flex-shrink:0;">
            <svg width="36" height="36" viewBox="58 20 50 65" xmlns="http://www.w3.org/2000/svg">
                <path d="M58 58 C58 48 65 42 72 42 C76 42 80 44 82 48 C84 44 88 42 92 42
                         C99 42 106 48 106 58 C106 70 82 82 82 82 C82 82 58 70 58 58Z"
                      fill="#f85149" opacity="0.25"/>
                <path d="M58 58 C58 48 65 42 72 42 C76 42 80 44 82 48 C84 44 88 42 92 42
                         C99 42 106 48 106 58 C106 70 82 82 82 82 C82 82 58 70 58 58Z"
                      fill="none" stroke="#f85149" stroke-width="1.8" stroke-linejoin="round"/>
                <polyline points="58,60 66,60 70,52 74,68 78,56 82,60 90,60 94,54 98,60 106,60"
                          fill="none" stroke="#f85149" stroke-width="2"
                          stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div>
            <div style="font-weight:800; font-size:1.1rem; color:#ffffff; letter-spacing:-0.02em;">
                HeartGuard
            </div>
            <div style="font-size:0.68rem; color:#8b949e; line-height:1.5; margin-top:2px;">
                AI-Powered Heart Failure<br>Risk Intelligence
            </div>
        </div>
    </div>
</div>
"""

SIDEBAR_NAV_CSS = """
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
"""

NAV_ITEMS = [
    ("🏠  Overview Dashboard",   "🏠  Overview Dashboard"),
    ("👤  Patient Review",        "👤  Patient Review"),
    ("📊  Model Performance",     "📊  Model Performance"),
    ("🎯  Feature Importance",    "🎯  Feature Importance"),
    ("🧪  Simulated Assessment",  "🧪  Simulated Assessment"),
    ("ℹ️  About / Project Info",  "ℹ️  About / Project Info"),
]


def render_sidebar() -> str:
    """Render the full sidebar and return the currently active page key."""
    with st.sidebar:
        st.markdown(SIDEBAR_LOGO_HTML, unsafe_allow_html=True)
        st.markdown(SIDEBAR_NAV_CSS,  unsafe_allow_html=True)

        if 'page' not in st.session_state:
            st.session_state.page = NAV_ITEMS[0][1]

        for label, key in NAV_ITEMS:
            is_active = st.session_state.page == key
            if is_active:
                st.markdown('<div class="nav-active">', unsafe_allow_html=True)
            if st.button(label, key=f"nav_{key}"):
                st.session_state.page = key
                st.rerun()
            if is_active:
                st.markdown('</div>', unsafe_allow_html=True)

        render_disclaimer_sidebar()

    return st.session_state.page