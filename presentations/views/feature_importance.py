import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.constants import (
    CLINICAL_CONTEXT, FEATURE_LABELS, IMPORTANCE_PATH, RISK_DIRECTION,
)
from utils.ui_components import render_page_header


# ── Chart ──────────────────────────────────────────────────────────────────────

def _render_importance_chart(importance_df: pd.DataFrame) -> None:
    st.markdown("""<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
        <span style="font-size:1rem;">📊</span>
        <span style="font-weight:600;color:#e6edf3;">Feature Importance (Top 10)</span>
    </div>""", unsafe_allow_html=True)

    sorted_df = importance_df.sort_values('Importance')
    max_imp   = sorted_df['Importance'].max()

    fig = go.Figure(go.Bar(
        x=sorted_df['Importance'],
        y=sorted_df['Feature'],
        orientation='h',
        marker=dict(
            color=list(range(len(sorted_df))),
            colorscale=[
                [0.0,  '#f85149'], [0.15, '#e3742c'], [0.3,  '#e3b341'],
                [0.45, '#3fb950'], [0.6,  '#39d0d8'], [0.75, '#58a6ff'],
                [0.9,  '#bc8cff'], [1.0,  '#f85149'],
            ],
            showscale=False,
        ),
        text=sorted_df['Importance'].round(4),
        textposition='outside',
        textfont=dict(color='#c9d1d9', size=10),
    ))
    fig.update_layout(
        yaxis_title=None,
        xaxis_title=(
            'Feature Importance Score<br>'
            '<span style="font-size:10px;color:#6e7681;">'
            '(Derived using Gini impurity reduction)</span>'
        ),
        margin=dict(t=10, b=50, l=10, r=55),
        height=380,
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        font_color="#c9d1d9",
        xaxis=dict(gridcolor="#30363d", range=[0, max_imp * 1.3], tickfont_size=10),
        yaxis=dict(gridcolor="#30363d", tickfont_size=11),
        showlegend=False,
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Full importance table ──────────────────────────────────────────────────────

def _render_importance_table(importance_df: pd.DataFrame) -> None:
    st.markdown("""<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
        <span style="font-size:1rem;">📋</span>
        <span style="font-weight:600;color:#e6edf3;">Full Importance Table</span>
    </div>""", unsafe_allow_html=True)

    rows_html = ""
    for rank, (_, row) in enumerate(
        importance_df.sort_values('Importance', ascending=False).iterrows(), 1
    ):
        feat = row['Feature']
        imp  = row['Importance']
        direction, dir_label = RISK_DIRECTION.get(feat, ('up', '—'))
        ctx_icon, ctx_label  = CLINICAL_CONTEXT.get(feat, ('📌', feat))

        # Shorten direction labels so they fit on one line
        short_label = {
            'Higher values associated with elevated risk': '↑ Higher = more risk',
            'Lower values associated with elevated risk':  '↓ Lower = more risk',
            'Presence associated with elevated risk':      'Presence = more risk',
        }.get(dir_label, dir_label)

        arrow_color = {'up': '#f85149', 'down': '#58a6ff', 'flag': '#e3b341'}.get(direction, '#8b949e')

        rows_html += f"""
        <tr>
            <td style="color:#6e7681;text-align:center;white-space:nowrap;padding:0.45rem 0.6rem;">{rank}</td>
            <td style="color:#e6edf3;font-weight:500;font-family:monospace;font-size:0.78rem;
                white-space:nowrap;padding:0.45rem 0.6rem;">{feat}</td>
            <td style="color:#c9d1d9;text-align:center;white-space:nowrap;padding:0.45rem 0.6rem;">{imp:.4f}</td>
            <td style="white-space:nowrap;padding:0.45rem 0.6rem;">
                <span style="color:{arrow_color};font-size:0.8rem;font-weight:600;">{short_label}</span>
            </td>
            <td style="color:#8b949e;font-size:0.78rem;white-space:nowrap;padding:0.45rem 0.6rem;">
                {ctx_icon} {ctx_label}
            </td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto;">
    <table class="styled-table" style="width:100%;table-layout:auto;">
        <thead>
            <tr>
                <th style="text-align:center;padding:0.4rem 0.6rem;white-space:nowrap;">Rank</th>
                <th style="padding:0.4rem 0.6rem;white-space:nowrap;">Feature</th>
                <th style="text-align:center;padding:0.4rem 0.6rem;white-space:nowrap;">Importance Score</th>
                <th style="padding:0.4rem 0.6rem;white-space:nowrap;">Risk Direction</th>
                <th style="padding:0.4rem 0.6rem;white-space:nowrap;">Clinical Context</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    </div>
    <div style="font-size:0.73rem;color:#6e7681;margin-top:0.6rem;">
        ℹ️ Scores are normalized and sum to 1. Higher scores indicate greater influence on the model's predictions.
    </div>""", unsafe_allow_html=True)


# ── Callout panels ─────────────────────────────────────────────────────────────

def _render_callouts(importance_df: pd.DataFrame) -> None:
    top3        = importance_df.nlargest(3, 'Importance')['Feature'].tolist()
    top3_labels = [FEATURE_LABELS.get(f, f).split(' (')[0] for f in top3]

    b1, b2 = st.columns(2)
    with b1:
        st.markdown(f"""
        <div class="section-card" style="height:100%;box-sizing:border-box;">
            <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                <div style="background:#12261e;border-radius:8px;padding:0.5rem;flex-shrink:0;">
                    <span style="font-size:1.25rem;">💡</span>
                </div>
                <div>
                    <div style="font-weight:600;margin-bottom:0.5rem;color:#3fb950;">Key Takeaway</div>
                    <div style="font-size:0.85rem;color:#c9d1d9;line-height:1.6;">
                        <b style="color:#e6edf3;">{', '.join(top3_labels)}</b> are the most influential
                        indicators in predicting adverse outcomes. These features were most frequently
                        used by the model to separate high-risk from low-risk patients.
                    </div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    with b2:
        st.markdown("""
        <div class="section-card" style="background:#1c1a10;border-color:#e3b34133;height:100%;box-sizing:border-box;">
            <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                <div style="background:#2a2010;border-radius:8px;padding:0.5rem;flex-shrink:0;">
                    <span style="font-size:1.25rem;">📋</span>
                </div>
                <div>
                    <div style="font-weight:600;margin-bottom:0.5rem;color:#e3b341;">Notes</div>
                    <ul style="font-size:0.82rem;color:#c9d1d9;line-height:1.8;margin:0;
                        padding-left:1.25rem;">
                        <li>Importance values are based on Gini impurity reduction across the
                            ensemble of decision trees.</li>
                        <li>Higher importance scores indicate stronger influence on model prediction
                            pathways.</li>
                        <li>Importance reflects statistical associations within the training data and
                            should not be interpreted as causal clinical relationships.</li>
                        <li>This model is intended for decision support and educational
                            purposes only.</li>
                    </ul>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="info-box" style="margin-top:1rem;">
        ℹ️ This analysis represents global model explainability.
        For patient-level explanations, please use the Simulated Patient Assessment module.
    </div>""", unsafe_allow_html=True)


# ── Public entry point ─────────────────────────────────────────────────────────

def render() -> None:
    render_page_header(
        "Feature Importance",
        "Top clinical indicators that contribute most to the model's prediction of adverse outcome.",
    )

    importance_df = pd.read_csv(IMPORTANCE_PATH)

    st.markdown("""<div class="info-box" style="margin-bottom:1.5rem;">
        <div>
            <b>ℹ️ Interpretation Guide:</b> Feature importance scores are derived from Gini
            impurity reduction across all decision trees in the model. Higher scores indicate
            stronger influence on the model's predictions. These reflect statistical associations,
            not clinical or epidemiological causation.
        </div>
    </div>""", unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1.15])
    with left_col:
        _render_importance_chart(importance_df)
    with right_col:
        _render_importance_table(importance_df)

    st.markdown("""<br>
    <style>
    /* Make callout columns equal height */
    div[data-testid="stHorizontalBlock"]:has(.section-card) > div[data-testid="column"] {
        display: flex;
        flex-direction: column;
    }
    div[data-testid="stHorizontalBlock"]:has(.section-card) > div[data-testid="column"] > div {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    div[data-testid="stHorizontalBlock"]:has(.section-card) > div[data-testid="column"] .section-card {
        flex: 1;
    }
    </style>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#1a0d0d;border:1px solid #f8514933;border-radius:10px;
         padding:1rem 1.25rem;margin-bottom:1.25rem;">
        <div style="display:flex;gap:0.75rem;align-items:flex-start;">
            <span style="font-size:1.25rem;flex-shrink:0;">⚠️</span>
            <div>
                <div style="font-weight:600;color:#f85149;margin-bottom:0.4rem;font-size:0.9rem;">
                    Association ≠ Causation
                </div>
                <div style="font-size:0.82rem;color:#c9d1d9;line-height:1.7;">
                    The feature importance scores on this page reflect how strongly each clinical
                    indicator is <b style="color:#e6edf3;">statistically associated</b> with adverse
                    outcomes in this dataset — they do <b style="color:#e6edf3;">not</b> imply that
                    any feature <i>causes</i> heart failure or death. Clinical decisions should
                    always be guided by qualified healthcare professionals and established medical
                    evidence.
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    _render_callouts(importance_df)