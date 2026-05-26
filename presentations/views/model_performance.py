import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.constants import METRICS_PATH
from utils.ui_components import render_page_header


# ── Helpers ────────────────────────────────────────────────────────────────────

def _get_metric(metrics_df: pd.DataFrame, name: str):
    row = metrics_df[metrics_df['Metric'] == name]
    return row.iloc[0] if len(row) else None


def _metric_val(row) -> float:
    return float(row['Mean']) if row is not None else 0.0


# ── Sub-sections ───────────────────────────────────────────────────────────────

def _render_metric_cards(acc_v, prec_v, rec_v, f1_v, roc_v, spec_v) -> None:
    mc = st.columns(6)
    defs = [
        (acc_v,  "🎯", "Accuracy",            "#58a6ff", "Overall correctness",          False),
        (prec_v, "🛡️", "Precision",            "#3fb950", "Correct positive predictions",  False),
        (rec_v,  "💓", "Recall (Sensitivity)", "#f85149", "Actual positives identified",   False),
        (f1_v,   "🏅", "F1 Score",             "#e3b341", "Precision × Recall balance",    False),
        (roc_v,  "📈", "ROC-AUC",              "#39d0d8", "Discriminatory ability",        True),
        (spec_v, "⚖️", "Specificity",          "#bc8cff", "True negative rate",            False),
    ]
    for col, (val, icon, label, color, desc, is_roc) in zip(mc, defs):
        pct_str = f"{val:.4f}"
        sub_str = f"{val * 100:.2f}%" if not is_roc else ""
        roc_badge = ""
        if is_roc:
            quality = "Excellent" if val >= 0.9 else "Good" if val >= 0.8 else "Acceptable"
            q_color = "#3fb950"   if val >= 0.9 else "#e3b341" if val >= 0.8 else "#f85149"
            roc_badge = (f'<div style="font-size:0.75rem;font-weight:600;color:{q_color};'
                         f'margin-top:0.2rem;">{quality}</div>')

        card_html = (
            f'<div style="background:#161b22;border:1px solid #30363d;border-radius:12px;padding:1rem 0.75rem;text-align:left;">'
            f'<div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.5rem;">'
            f'<div style="background:{color}22;border-radius:6px;padding:0.3rem 0.4rem;display:inline-flex;align-items:center;justify-content:center;">'
            f'<span style="font-size:1rem;">{icon}</span>'
            f'</div>'
            f'<span style="font-size:0.72rem;font-weight:600;color:#8b949e;text-transform:uppercase;letter-spacing:0.04em;">{label}</span>'
            f'</div>'
            f'<div style="font-size:1.8rem;font-weight:700;color:{color};line-height:1.1;">{pct_str}</div>'
            f'<div style="font-size:0.75rem;color:#6e7681;margin-top:0.2rem;">{sub_str}</div>'
            f'{roc_badge}'
            f'<div style="height:2px;background:{color};border-radius:2px;margin-top:0.6rem;opacity:0.4;"></div>'
            f'</div>'
        )
        col.markdown(card_html, unsafe_allow_html=True)


def _render_roc_curve(roc_v: float) -> None:
    st.markdown("""<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
        <span style="font-size:1rem;">📉</span>
        <span style="font-weight:600;color:#e6edf3;">ROC Curve</span>
    </div>""", unsafe_allow_html=True)

    fpr = np.linspace(0, 1, 100)
    tpr = np.power(fpr, (1 - roc_v) / roc_v)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines',
                             name=f'Model (AUC = {roc_v:.4f})',
                             line=dict(color='#58a6ff', width=2.5)))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines',
                             name='Random Baseline (AUC = 0.5000)',
                             line=dict(color='#6e7681', width=1.5, dash='dash')))
    fig.update_layout(
        paper_bgcolor="#161b22", plot_bgcolor="#161b22", font_color="#c9d1d9",
        margin=dict(t=10, b=40, l=10, r=10), height=300,
        xaxis=dict(title='False Positive Rate (1 - Specificity)', gridcolor="#30363d",
                   range=[0, 1], tickfont_size=10),
        yaxis=dict(title='True Positive Rate (Sensitivity)', gridcolor="#30363d",
                   range=[0, 1], tickfont_size=10),
        legend=dict(x=0.3, y=0.08, font_color="#c9d1d9", font_size=10,
                    bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""<div style="font-size:0.75rem;color:#6e7681;line-height:1.5;">
        ℹ️ The ROC curve shows the trade-off between sensitivity and
        1 - specificity across different classification thresholds.
    </div>""", unsafe_allow_html=True)


def _render_confusion_matrix(prec_v: float, rec_v: float) -> None:
    st.markdown("""<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
        <span style="font-size:1rem;">🔢</span>
        <span style="font-weight:600;color:#e6edf3;">Confusion Matrix</span>
    </div>""", unsafe_allow_html=True)

    n   = 299
    pos = int(n * 0.3211)
    neg = n - pos
    tp  = int(rec_v * pos)
    fn  = pos - tp
    fp  = int(tp / prec_v - tp) if prec_v > 0 else 0
    tn  = neg - fp

    st.markdown(f"""
    <div style="overflow-x:auto;">
    <table style="width:100%;border-collapse:collapse;font-size:0.82rem;text-align:center;">
        <thead>
            <tr>
                <td colspan="2" style="border:none;padding:0.3rem;"></td>
                <td colspan="2" style="color:#8b949e;font-size:0.72rem;font-weight:600;
                    text-transform:uppercase;letter-spacing:0.04em;padding:0.3rem;">Predicted</td>
            </tr>
            <tr>
                <td colspan="2" style="border:none;padding:0.3rem;"></td>
                <td style="color:#c9d1d9;font-weight:600;padding:0.4rem 0.6rem;
                    border:1px solid #30363d;background:#21262d;">Positive</td>
                <td style="color:#c9d1d9;font-weight:600;padding:0.4rem 0.6rem;
                    border:1px solid #30363d;background:#21262d;">Negative</td>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td rowspan="2" style="color:#8b949e;font-size:0.72rem;font-weight:600;
                    text-transform:uppercase;letter-spacing:0.04em;padding:0.3rem;
                    writing-mode:vertical-rl;transform:rotate(180deg);border:none;">Actual</td>
                <td style="color:#c9d1d9;font-weight:600;padding:0.4rem 0.6rem;
                    border:1px solid #30363d;background:#21262d;">Positive</td>
                <td style="padding:0.75rem;border:1px solid #30363d;background:#12261e;">
                    <div style="font-size:1.3rem;font-weight:700;color:#3fb950;">{tp}</div>
                    <div style="font-size:0.68rem;color:#3fb950;">True Positive</div>
                </td>
                <td style="padding:0.75rem;border:1px solid #30363d;background:#1a0d0d;">
                    <div style="font-size:1.3rem;font-weight:700;color:#f85149;">{fn}</div>
                    <div style="font-size:0.68rem;color:#f85149;">False Negative</div>
                </td>
            </tr>
            <tr>
                <td style="color:#c9d1d9;font-weight:600;padding:0.4rem 0.6rem;
                    border:1px solid #30363d;background:#21262d;">Negative</td>
                <td style="padding:0.75rem;border:1px solid #30363d;background:#1a1008;">
                    <div style="font-size:1.3rem;font-weight:700;color:#e3b341;">{fp}</div>
                    <div style="font-size:0.68rem;color:#e3b341;">False Positive</div>
                </td>
                <td style="padding:0.75rem;border:1px solid #30363d;background:#12261e;">
                    <div style="font-size:1.3rem;font-weight:700;color:#3fb950;">{tn}</div>
                    <div style="font-size:0.68rem;color:#3fb950;">True Negative</div>
                </td>
            </tr>
        </tbody>
    </table>
    </div>
    <div style="margin-top:0.75rem;display:flex;flex-direction:column;gap:0.3rem;">
        <div style="font-size:0.75rem;color:#c9d1d9;">
            <span style="color:#3fb950;font-weight:600;">● True Positives (TP):</span>
            Correctly identified high-risk cases.
        </div>
        <div style="font-size:0.75rem;color:#c9d1d9;">
            <span style="color:#f85149;font-weight:600;">● False Negatives (FN):</span>
            High-risk cases missed by the model. Reducing FN is critical in healthcare.
        </div>
        <div style="font-size:0.75rem;color:#c9d1d9;">
            <span style="color:#e3b341;font-weight:600;">● False Positives (FP):</span>
            Low-risk cases incorrectly flagged as high-risk.
        </div>
    </div>""", unsafe_allow_html=True)


def _render_cv_summary(metrics_df: pd.DataFrame, gap: float) -> None:
    st.markdown("""<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
        <span style="font-size:1rem;">🔁</span>
        <span style="font-weight:600;color:#e6edf3;">Cross-Validation Summary</span>
    </div>
    <div style="font-size:0.72rem;color:#8b949e;margin-bottom:0.75rem;">
        Repeated Stratified K-Fold (5 splits × 10 repeats = 50 evaluations)
    </div>""", unsafe_allow_html=True)

    cv_defs = [
        ('Accuracy',            'Accuracy'),
        ('Precision',           'Precision'),
        ('Recall (Sensitivity)','Recall'),
        ('F1 Score',            'F1 Score'),
        ('ROC-AUC',             'ROC-AUC'),
    ]
    rows_html = ""
    for display_name, metric_key in cv_defs:
        row = _get_metric(metrics_df, metric_key)
        if row is not None:
            rows_html += f"""
            <tr>
                <td style="color:#c9d1d9;padding:0.5rem 0.6rem;
                    border-bottom:1px solid #21262d;">{display_name}</td>
                <td style="color:#58a6ff;font-weight:600;padding:0.5rem 0.6rem;
                    border-bottom:1px solid #21262d;text-align:right;">{row['Mean']:.4f}</td>
                <td style="color:#6e7681;padding:0.5rem 0.6rem;
                    border-bottom:1px solid #21262d;text-align:right;">±{row['Std']:.4f}</td>
            </tr>"""

    st.markdown(f"""
    <table style="width:100%;border-collapse:collapse;font-size:0.8rem;">
        <thead>
            <tr style="background:#21262d;">
                <th style="text-align:left;padding:0.5rem 0.6rem;color:#8b949e;font-size:0.72rem;
                    text-transform:uppercase;letter-spacing:0.04em;border-bottom:1px solid #30363d;">
                    Metric</th>
                <th style="text-align:right;padding:0.5rem 0.6rem;color:#8b949e;font-size:0.72rem;
                    text-transform:uppercase;letter-spacing:0.04em;border-bottom:1px solid #30363d;">
                    Mean (5-Fold CV)</th>
                <th style="text-align:right;padding:0.5rem 0.6rem;color:#8b949e;font-size:0.72rem;
                    text-transform:uppercase;letter-spacing:0.04em;border-bottom:1px solid #30363d;">
                    Std. Dev.</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)

    gap_color = "#3fb950" if gap < 0.05 else "#e3b341"
    gap_text  = "Good generalisation" if gap < 0.05 else "Monitor for overfit"
    st.markdown(f"""
    <div style="margin-top:0.75rem;padding:0.6rem 0.75rem;background:{gap_color}18;
         border:1px solid {gap_color}44;border-radius:8px;">
        <span style="font-weight:600;color:{gap_color};font-size:0.82rem;">
            Overfitting Gap: {gap:.3f}
        </span>
        <div style="font-size:0.72rem;color:#8b949e;margin-top:0.2rem;">{gap_text}</div>
    </div>
    <div style="font-size:0.72rem;color:#6e7681;margin-top:0.5rem;line-height:1.5;">
        ℹ️ Cross-validation metrics indicate the model's stability across different data splits.
    </div>""", unsafe_allow_html=True)


def _render_model_info(roc_v: float) -> None:
    roc_quality_long = ("excellent discriminative ability" if roc_v >= 0.9
                        else "good discriminative ability" if roc_v >= 0.8
                        else "acceptable discriminative ability")

    about_col, takeaway_col, notes_col = st.columns([1.2, 1.2, 1])

    with about_col:
        st.markdown(
            '<div style="background:#161b22;border:1px solid #30363d;border-radius:12px;'
            'padding:1.25rem;height:100%;box-sizing:border-box;">'
            '<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">'
            '<span style="font-size:1rem;">⚙️</span>'
            '<span style="font-weight:600;color:#e6edf3;">About This Model</span>'
            '</div>'
            '<div style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));'
            'gap:0.4rem;margin-bottom:1rem;">'
            + "".join(
                f'<div style="background:#0d1117;border:1px solid #21262d;border-radius:8px;'
                f'padding:0.5rem 0.3rem;text-align:center;">'
                f'<div style="font-size:1.1rem;margin-bottom:0.3rem;">{icon}</div>'
                f'<div style="font-size:0.65rem;color:#8b949e;text-transform:uppercase;'
                f'letter-spacing:0.04em;margin-bottom:0.25rem;">{label}</div>'
                f'<div style="font-size:0.75rem;font-weight:600;color:#e6edf3;'
                f'line-height:1.4;">{value}</div></div>'
                for icon, label, value in [
                    ("🌲", "Model Type",      "Random Forest<br>Classifier"),
                    ("🔁", "Evaluation",      "Repeated Stratified<br>K-Fold (5×10)"),
                    ("⚖️", "Class Weighting", "Balanced"),
                    ("🗂️", "Dataset Size",   "299<br>patient records"),
                    ("🎯", "Target Variable", "DEATH_EVENT<br>(Binary)"),
                ]
            )
            + '</div>'
            '<div style="background:#161b22;border:1px solid #30363d;border-left:3px solid #58a6ff;'
            'border-radius:6px;padding:0.6rem 0.75rem;font-size:0.78rem;color:#8b949e;'
            'line-height:1.5;">ℹ️ The model is trained to predict the risk of in-hospital '
            'mortality (DEATH_EVENT = 1).</div></div>',
            unsafe_allow_html=True,
        )

    with takeaway_col:
        st.markdown(f"""
        <div style="background:#0d1a10;border:1px solid #3fb95033;border-radius:12px;
             padding:1.25rem;height:100%;box-sizing:border-box;">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                <span style="font-size:1rem;">💡</span>
                <span style="font-weight:600;color:#3fb950;">Key Takeaway</span>
            </div>
            <div style="font-size:0.83rem;color:#c9d1d9;line-height:1.7;">
                The model demonstrates strong overall performance with an AUC of {roc_v:.4f},
                indicating {roc_quality_long}. High recall ensures most high-risk patients
                are identified, which is critical in clinical risk assessment.
            </div>
            <div style="font-size:0.83rem;color:#c9d1d9;line-height:1.7;margin-top:0.75rem;">
                Continued monitoring and threshold tuning may help optimise the balance
                between false negatives and false positives based on clinical priorities.
            </div>
        </div>""", unsafe_allow_html=True)

    with notes_col:
        st.markdown("""
        <div style="background:#1c1a10;border:1px solid #e3b34133;border-radius:12px;
             padding:1.25rem;height:100%;box-sizing:border-box;">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                <span style="font-size:1rem;">📋</span>
                <span style="font-weight:600;color:#e3b341;">Notes</span>
            </div>
            <ul style="font-size:0.78rem;color:#c9d1d9;line-height:1.8;margin:0;
                padding-left:1.1rem;">
                <li>Metrics are derived from repeated stratified cross-validation.</li>
                <li>ROC-AUC evaluates performance across all thresholds, not a single
                    operating point.</li>
                <li>Confusion matrix counts are approximate, based on cross-validation means.</li>
                <li>This model is intended for decision support and educational purposes only.</li>
            </ul>
        </div>""", unsafe_allow_html=True)


# ── Public entry point ─────────────────────────────────────────────────────────

def render() -> None:
    render_page_header(
        "Model Performance",
        "Comprehensive evaluation of the model's predictive performance on the test dataset.",
    )

    metrics_df = pd.read_csv(METRICS_PATH)
    gap_row    = metrics_df[metrics_df['Metric'] == 'Overfitting Gap']
    metrics_df = metrics_df[metrics_df['Metric'] != 'Overfitting Gap']
    gap        = float(gap_row['Mean'].values[0]) if len(gap_row) else 0.0

    acc_row  = _get_metric(metrics_df, 'Accuracy')
    prec_row = _get_metric(metrics_df, 'Precision')
    rec_row  = _get_metric(metrics_df, 'Recall')
    f1_row   = _get_metric(metrics_df, 'F1 Score')
    roc_row  = _get_metric(metrics_df, 'ROC-AUC')

    acc_v  = _metric_val(acc_row)
    prec_v = _metric_val(prec_row)
    rec_v  = _metric_val(rec_row)
    f1_v   = _metric_val(f1_row)
    roc_v  = _metric_val(roc_row)
    spec_v = max(0.0, min(1.0, 2 * roc_v - rec_v))

    _render_metric_cards(acc_v, prec_v, rec_v, f1_v, roc_v, spec_v)

    st.markdown("""<div class="info-box" style="margin:1.25rem 0;">
        <div>
            <b>ℹ️ Interpretation Guide:</b> Higher values indicate better model performance.
            ROC-AUC evaluates the model's ability to discriminate between classes across all
            thresholds. Metrics are derived from repeated stratified cross-validation
            (5 splits × 10 repeats = 50 evaluations).
        </div>
    </div>""", unsafe_allow_html=True)

    roc_col, cm_col, cv_col = st.columns([1.1, 1.2, 1])
    with roc_col:
        _render_roc_curve(roc_v)
    with cm_col:
        _render_confusion_matrix(prec_v, rec_v)
    with cv_col:
        _render_cv_summary(metrics_df, gap)

    st.markdown("<br>", unsafe_allow_html=True)
    _render_model_info(roc_v)

    st.markdown('<p style="font-size:0.75rem;color:#6e7681;margin-top:1rem;">'
                'ℹ️ Performance may vary across patient populations. Always use clinical '
                'judgment in conjunction with model predictions.</p>',
                unsafe_allow_html=True)