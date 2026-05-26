import streamlit as st

from utils.ui_components import render_footer, render_page_header


def render() -> None:
    render_page_header(
        "About / Project Info",
        "Learn more about the dataset, methodology, AI model, and technology used in this project.",
    )

    c1, c2, c3 = st.columns(3)

    # ── Dataset Information ────────────────────────────────────────────────────
    with c1:
        st.markdown("""
        <div class="section-card">
            <div style="display:flex;gap:0.75rem;align-items:center;margin-bottom:1rem;">
                <div style="background:#0d1b2a;border-radius:8px;padding:0.5rem;font-size:1.25rem;">🗄️</div>
                <b style="color:#e6edf3;">1. Dataset Information</b>
            </div>
            <div style="font-size:0.85rem;color:#8b949e;margin-bottom:1rem;">
                The model is built using the Heart Failure Clinical Records Dataset.
            </div>
            <table class="styled-table" style="table-layout:fixed;width:100%;">
                <colgroup>
                    <col style="width:38%;">
                    <col style="width:62%;">
                </colgroup>
                <tbody>
                    <tr>
                        <td style="color:#8b949e;vertical-align:top;">Source</td>
                        <td><b style="color:#e6edf3;">Kaggle</b></td>
                    </tr>
                    <tr>
                        <td style="color:#8b949e;vertical-align:top;">File</td>
                        <td style="word-break:break-all;overflow-wrap:anywhere;">
                            <b style="color:#e6edf3;font-size:0.78rem;">
                                heart_failure_clinical_records_dataset.csv
                            </b>
                        </td>
                    </tr>
                    <tr>
                        <td style="color:#8b949e;vertical-align:top;">Total Records</td>
                        <td><b style="color:#e6edf3;">299</b></td>
                    </tr>
                    <tr>
                        <td style="color:#8b949e;vertical-align:top;">Features</td>
                        <td><b style="color:#e6edf3;">11 clinical indicators</b></td>
                    </tr>
                    <tr>
                        <td style="color:#8b949e;vertical-align:top;">Target Variable</td>
                        <td><b style="color:#e6edf3;">DEATH_EVENT (1 = Death, 0 = Survived)</b></td>
                    </tr>
                </tbody>
            </table>
            <div class="info-box" style="margin-top:1rem;">
                ℹ️ This dataset contains de-identified patient clinical records.
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Methodology ────────────────────────────────────────────────────────────
    with c2:
        steps = [
            ("Data Loading & Validation",     "Load and validate the clinical dataset."),
            ("Data Preprocessing",            "Handle missing values, encode variables, prepare features."),
            ("Model Training",                "Train Random Forest on full dataset after cross-validation."),
            ("Model Evaluation",              "Evaluate performance using repeated stratified K-fold."),
            ("Risk Scoring & Categorization", "Generate risk probability and categorize into Low / Medium / High."),
            ("Recommendation Engine",         "Provide risk-aware recommendations and explanations."),
        ]

        steps_html = "".join(
            f'<div style="display:flex;gap:0.75rem;margin-bottom:0.75rem;align-items:flex-start;">'
            f'<div style="background:#3fb950;color:#0d1117;border-radius:50%;width:22px;height:22px;'
            f'display:flex;align-items:center;justify-content:center;font-size:0.72rem;'
            f'font-weight:700;flex-shrink:0;margin-top:2px;">{i}</div>'
            f'<div>'
            f'<div style="font-weight:600;font-size:0.85rem;color:#e6edf3;">{title}</div>'
            f'<div style="font-size:0.8rem;color:#8b949e;">{desc}</div>'
            f'</div></div>'
            for i, (title, desc) in enumerate(steps, 1)
        )

        st.markdown(f"""
        <div class="section-card">
            <div style="display:flex;gap:0.75rem;align-items:center;margin-bottom:1rem;">
                <div style="background:#12261e;border-radius:8px;padding:0.5rem;font-size:1.25rem;">⚙️</div>
                <b style="color:#e6edf3;">2. Methodology</b>
            </div>
            <div style="font-size:0.85rem;color:#8b949e;margin-bottom:1rem;">
                End-to-end workflow for building this risk stratification system.
            </div>
            {steps_html}
        </div>""", unsafe_allow_html=True)

    # ── AI Model Details ───────────────────────────────────────────────────────
    with c3:
        st.markdown("""
        <div class="section-card">
            <div style="display:flex;gap:0.75rem;align-items:center;margin-bottom:1rem;">
                <div style="background:#1a1030;border-radius:8px;padding:0.5rem;font-size:1.25rem;">🧠</div>
                <b style="color:#e6edf3;">3. AI Model Details</b>
            </div>
            <table class="styled-table" style="table-layout:fixed;width:100%;">
                <colgroup>
                    <col style="width:42%;">
                    <col style="width:58%;">
                </colgroup>
                <tbody>
                    <tr>
                        <td style="color:#8b949e;vertical-align:top;">Model</td>
                        <td><b style="color:#e6edf3;">Random Forest</b></td>
                    </tr>
                    <tr>
                        <td style="color:#8b949e;vertical-align:top;">Type</td>
                        <td><b style="color:#e6edf3;">Binary Classification</b></td>
                    </tr>
                    <tr>
                        <td style="color:#8b949e;vertical-align:top;">Target</td>
                        <td style="word-break:break-word;">
                            <b style="color:#e6edf3;">DEATH_EVENT (1=Death, 0=Survived)</b>
                        </td>
                    </tr>
                    <tr>
                        <td style="color:#8b949e;vertical-align:top;">Training</td>
                        <td style="word-break:break-word;">
                            <b style="color:#e6edf3;">scikit-learn RandomForestClassifier</b>
                        </td>
                    </tr>
                    <tr>
                        <td style="color:#8b949e;vertical-align:top;">Evaluation</td>
                        <td style="word-break:break-word;">
                            <b style="color:#e6edf3;">Accuracy, Precision, Recall, F1, AUC-ROC</b>
                        </td>
                    </tr>
                    <tr>
                        <td style="color:#8b949e;vertical-align:top;">Feature Importance</td>
                        <td><b style="color:#e6edf3;">Gini impurity reduction</b></td>
                    </tr>
                    <tr>
                        <td style="color:#8b949e;vertical-align:top;">Class Weighting</td>
                        <td><b style="color:#e6edf3;">Balanced</b></td>
                    </tr>
                    <tr>
                        <td style="color:#8b949e;vertical-align:top;">Trained On</td>
                        <td><b style="color:#e6edf3;">Historical clinical records</b></td>
                    </tr>
                </tbody>
            </table>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#1c1a10;border:1px solid #e3b34133;border-radius:10px;
         padding:1.25rem 1.5rem;margin-bottom:1.5rem;">
        <div style="font-weight:600;color:#e3b341;margin-bottom:0.4rem;">⚠️ Important Disclaimer</div>
        <div style="font-size:0.85rem;color:#c9d1d9;line-height:1.6;">
            This application is intended for educational and research purposes only. It is a
            decision-support tool and not a substitute for professional medical judgment. Always
            consult qualified healthcare professionals for medical advice, diagnosis, and treatment.
        </div>
    </div>""", unsafe_allow_html=True)

    tech_col, how_col = st.columns(2)

    with tech_col:
        st.markdown("""
        <div class="section-card">
            <div style="display:flex;gap:0.75rem;align-items:center;margin-bottom:1rem;">
                <span style="font-size:1.1rem;">💻</span>
                <b style="color:#e6edf3;">4. Technology Stack</b>
            </div>
            <div style="display:flex;gap:1.5rem;flex-wrap:wrap;font-size:0.82rem;color:#c9d1d9;">
                <div style="text-align:center;">
                    <div style="font-size:1.5rem;">🐍</div>
                    <b style="color:#e6edf3;">Python</b><br>
                    <span style="color:#6e7681;">3.10+</span>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.5rem;">🎈</div>
                    <b style="color:#e6edf3;">Streamlit</b><br>
                    <span style="color:#6e7681;">1.30+</span>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.5rem;">🤖</div>
                    <b style="color:#e6edf3;">scikit-learn</b><br>
                    <span style="color:#6e7681;">1.4+</span>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.5rem;">🐼</div>
                    <b style="color:#e6edf3;">pandas</b><br>
                    <span style="color:#6e7681;">2.2+</span>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.5rem;">🔢</div>
                    <b style="color:#e6edf3;">NumPy</b><br>
                    <span style="color:#6e7681;">1.26+</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    with how_col:
        st.markdown("""
        <div class="section-card">
            <div style="display:flex;gap:0.75rem;align-items:center;margin-bottom:1rem;">
                <span style="font-size:1.1rem;">📖</span>
                <b style="color:#e6edf3;">5. How to Use This App</b>
            </div>
            <div style="font-size:0.85rem;color:#c9d1d9;line-height:1.8;">
                <div>✅ Explore the dashboard for key insights and risk distribution.</div>
                <div>✅ Review individual patient records and model predictions.</div>
                <div>✅ Analyze model performance and feature importance.</div>
                <div>✅ Use the simulated assessment to evaluate patient scenarios.</div>
            </div>
        </div>""", unsafe_allow_html=True)

    render_footer("© 2025 All rights reserved")