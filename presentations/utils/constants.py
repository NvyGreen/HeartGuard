import os
from datetime import date

BASE_DIR          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_PATH      = os.path.join(BASE_DIR, '..', 'notebooks', 'metrics.csv')
IMPORTANCE_PATH   = os.path.join(BASE_DIR, '..', 'notebooks', 'feature_importance.csv')
PREDICTIONS_PATH  = os.path.join(BASE_DIR, '..', 'notebooks', 'predictions.csv')
PIPELINE_PATH     = os.path.join(BASE_DIR, '..', 'notebooks', 'pipeline.pkl')
DATA_PATH         = os.path.join(BASE_DIR, '..', 'data', 'heart_failure_clinical_records_dataset.csv')

RISK_THRESHOLDS = {"HIGH": 0.7, "MEDIUM": 0.4}
RISK_COLORS     = {"HIGH": "#f85149", "MEDIUM": "#e3b341", "LOW": "#3fb950"}
RISK_LABELS     = {"HIGH": "High Risk", "MEDIUM": "Medium Risk", "LOW": "Low Risk"}

FEATURES = [
    'age', 'anaemia', 'creatinine_phosphokinase', 'diabetes',
    'ejection_fraction', 'high_blood_pressure', 'platelets',
    'serum_creatinine', 'serum_sodium', 'sex', 'smoking',
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

RISK_DIRECTION = {
    'serum_creatinine':         ('up',   'Higher values associated with elevated risk'),
    'ejection_fraction':        ('down', 'Lower values associated with elevated risk'),
    'age':                      ('up',   'Higher values associated with elevated risk'),
    'serum_sodium':             ('down', 'Lower values associated with elevated risk'),
    'creatinine_phosphokinase': ('up',   'Higher values associated with elevated risk'),
    'platelets':                ('down', 'Lower values associated with elevated risk'),
    'sex':                      ('up',   'Higher values associated with elevated risk'),
    'high_blood_pressure':      ('flag', 'Presence associated with elevated risk'),
    'anaemia':                  ('flag', 'Presence associated with elevated risk'),
    'smoking':                  ('flag', 'Presence associated with elevated risk'),
    'diabetes':                 ('flag', 'Presence associated with elevated risk'),
}

CLINICAL_CONTEXT = {
    'serum_creatinine':         ('🫀', 'Kidney function indicator'),
    'ejection_fraction':        ('❤️', 'Cardiac pumping efficiency'),
    'age':                      ('🧑', 'Patient age (risk increases with age)'),
    'serum_sodium':             ('💧', 'Electrolyte balance indicator'),
    'creatinine_phosphokinase': ('💜', 'Muscle enzyme / tissue stress'),
    'platelets':                ('⭕', 'Blood component / clotting indicator'),
    'sex':                      ('⚧',  'Biological sex'),
    'high_blood_pressure':      ('🩺', 'History of hypertension'),
    'anaemia':                  ('🔴', 'Reduced blood oxygen-carrying capacity'),
    'smoking':                  ('🚬', 'Smoking status'),
    'diabetes':                 ('🩸', 'Blood sugar regulation'),
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#161b22",
    plot_bgcolor="#161b22",
    font_color="#c9d1d9",
    margin=dict(t=10, b=10, l=10, r=10),
    height=280,
    showlegend=True,
)

TODAY = date.today().strftime("%b %d, %Y")