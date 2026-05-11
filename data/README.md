
### 1. Stroke Prediction
File: `healthcare-dataset-stroke-data.csv`  
Link: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset
Collected from a healthcare provider, this dataset contains patient information used to predict whether a patient is likely to have a stroke. Each row represents one patient and includes demographic and clinical attributes.

**Key features:**
`age`, `gender`, `ever_married`, `work_type`, `Residence_type`
`hypertension`, `heart_disease`
`avg_glucose_level`, `bmi`
`smoking_status`
Target: `stroke` — 0 (no stroke) or 1 (stroke)

**Things to be aware of:**

Around 200 rows have missing BMI values

Only ~5% of patients had a stroke — the dataset is heavily imbalanced

### 2. Heart Failure Clinical Data
File: `heart_failure_clinical_records_dataset.csv`  
Link: https://www.kaggle.com/datasets/andrewmvd/heart-failure-clinical-data
Based on a study from the Faisalabad Institute of Cardiology, this dataset contains medical records of 299 heart failure patients collected during their follow-up period. The goal is to predict whether a patient will survive.

**Key features:**
`age`, `sex`, `smoking`
`ejection_fraction` — percentage of blood leaving the heart per contraction
`serum_creatinine`, `serum_sodium` — kidney function markers
`creatinine_phosphokinase`, `platelets`
`anaemia`, `diabetes`, `high_blood_pressure`
`time` — length of follow-up period in days
Target: `DEATH_EVENT` — 0 (survived) or 1 (died)

**Things to be aware of:**

No missing values
Small dataset (299 rows) — consider cross-validation over a single train/test split

The `time` column is the follow-up duration, not a clinical feature available at admission — think carefully about whether to include it

### 3. MIMIC-IV Style ICU Dataset — Sepsis Prediction
File: (verify exact filename on the Kaggle page)  
Link: https://www.kaggle.com/datasets/sinanshereef/mimic-iv-style-icu-dataset-for-sepsis-prediction
Modeled after the MIMIC-IV clinical database, this dataset contains ICU patient records with vital signs and lab results. The goal is to predict whether a patient will develop sepsis during their ICU stay.

**Key features:**
Vitals: `heart_rate`, `resp_rate`, `sbp`, `dbp`, `spo2`, `temperature`
Labs: `lactate`, `wbc`, `creatinine`, `bilirubin`
`sofa_score`, `age`, `gender`, `icu_los`
Target: `sepsis_label` — 0 (no sepsis) or 1 (sepsis) (verify column name on Kaggle)

**Things to be aware of:**

Lab columns have significant missing values

Dataset may have multiple rows per patient (time series) — check before modeling

Sepsis is a minority class — class imbalance needs to be addressed

### 4. Medical Appointment No-Shows
File: `KaggleV2-May-2016.csv`  
Link: https://www.kaggle.com/datasets/joniarroba/noshowappointments
This dataset contains records of over 110,000 medical appointments from Brazilian public hospitals in 2016. The goal is to predict whether a patient will show up for their scheduled appointment.

**Key features:**
`Age`, `Gender`
`ScheduledDay`, `AppointmentDay` — useful for engineering a wait-time feature
`Neighbourhood`
`Scholarship` — whether the patient is on a welfare program
`Hypertension`, `Diabetes`, `Alcoholism`, `Handicap`
`SMS_Received` — whether the patient received a reminder SMS
Target: `No-show` — "Yes" (missed) or "No" (showed up)

**Things to be aware of:**

The original dataset has column name typos: `Hipertension` and `Handcap` — the notebook fixes these automatically

One patient record has an age of -1 — filter it out

`Neighbourhood` has 80+ unique values — think carefully about how to encode it

The date columns need to be parsed and engineered into useful features (e.g. days between scheduling and appointment)

### 5. Hospital Triage & Patient History
File: (verify exact filename on the Kaggle page)  
Link: https://www.kaggle.com/datasets/maalona/hospital-triage-and-patient-history-data
Based on data from the Yale New Haven Hospital emergency department, this is a very wide dataset with nearly 1,000 features per patient visit. It includes triage information, past medical history, prior lab results, and outpatient medication history. The goal is to predict whether a patient will be admitted to the hospital at triage.

**Key features:**
`esi` — Emergency Severity Index (1 = most severe, 5 = least severe)
Triage vitals: heart rate, respiratory rate, blood pressure, SpO2, temperature
Arrival mode, age, gender, insurance
Past medical history encoded as ICD-9 CCS categories
Prior lab values and imaging counts
Outpatient medication categories
Target: `disposition` — admitted vs. discharged (verify exact values on Kaggle)

**Things to be aware of:**

~972 total columns — feature selection is essential

Many columns have high missingness, especially lab and imaging history

ESI alone is a strong predictor — a good starting baseline

Start with a small curated feature set and expand from there

### 6. Hospital Readmission Risk Prediction (2026)
File: (verify exact filename on the Kaggle page)  
Link: https://www.kaggle.com/datasets/algozee/hospital-readmission-risk-prediction-2026
A 2026 synthetic dataset containing patient demographic, clinical, and administrative information recorded at the time of hospital discharge. The goal is to predict whether a patient will be readmitted within 30 days.

**Key features:**
`age`, `gender`, `insurance_type`
`primary_diagnosis`, `number_diagnoses`
`time_in_hospital`, `num_procedures`, `num_medications`, `num_lab_procedures`
`discharge_disposition`
Target: `readmitted` — 0 (not readmitted within 30 days) or 1 (readmitted) (verify on Kaggle)

**Things to be aware of:**

New dataset — inspect the columns carefully after loading as they may differ from what is listed above

Watch out for leakage: some features may only be known after readmission, not at discharge

Hospitals are financially penalized for high readmission rates, which affects how you should think about your evaluation metric
