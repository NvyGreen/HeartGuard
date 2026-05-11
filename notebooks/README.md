# Notebooks

This folder contains a starter template notebook for each dataset. Each template loads the data and provides a basic structure to work from — the rest is up to you.

---

## Setup

Make sure you have the following installed before running any notebook:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn imbalanced-learn
```

If you are using Google Colab, these are already available except for `imbalanced-learn`:

```bash
pip install imbalanced-learn
```

---

## Before You Run

Download your dataset from Kaggle and place the CSV in the `datasets/` folder. The notebooks reference the files using a relative path (`../datasets/filename.csv`), so the folder structure should look like this:

```
project/
├── datasets/
│   └── your_dataset.csv
└── notebooks/
    └── your_notebook.ipynb
```

---

## Templates

| Notebook | Dataset |
|----------|---------|
| `stroke_prediction/template_stroke.ipynb` | Stroke Prediction |
| `heart_failure/template_heart_failure.ipynb` | Heart Failure Clinical Data |
| `mimic_icu_sepsis/template_sepsis_icu.ipynb` | MIMIC-IV Style ICU — Sepsis |
| `noshow_appointments/template_noshow.ipynb` | Medical Appointment No-Shows |
| `hospital_triage/template_triage.ipynb` | Hospital Triage & Patient History |
| `hospital_readmission/template_readmission.ipynb` | Hospital Readmission Risk (2026) |

Each template follows the same structure: **Imports → Load Data → EDA → Preprocessing → Model → Evaluation**. The load cell is pre-filled. Use the `# TODO` comments and discussion questions throughout as a guide for what to build.
