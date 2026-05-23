## Clinical Problem
Heart failure patients are at risk of serious complications and rapid clinical deterioration, but identifying high-risk patients early can be difficult when clinicians must review many clinical variables manually. Delayed identification of elevated-risk patients may impact timely monitoring, escalation, and follow-up decisions.

## Current Workflow
Clinicians review patient vitals, lab results, and clinical history manually to assess risk severity. Risk assessment depends heavily on physician experience and interpretation of multiple factors such as ejection fraction, serum creatinine, sodium levels, diabetes status, and age. Historical outcome patterns are not systematically analyzed to support prioritization or monitoring decisions.

## Proposed AI Solution
Build a Heart Failure Risk Stratification & Recommendation System that uses machine learning to identify patients whose clinical patterns resemble historical higher-risk cases. The system analyzes patient clinical indicators and historical outcome patterns, including follow-up duration and adverse outcomes, to categorize patients into Low, Medium, or High risk groups. The system generates explainable risk insights and rule-based recommendations such as routine follow-up, closer monitoring, or urgent clinical review consideration. The system is intended for educational and decision-support demonstration purposes only and is not designed to replace clinical judgment or provide medical diagnosis.

## Workflow Integration
The AI system acts as a decision-support layer after patient clinical data becomes available. The model evaluates patient severity using clinical indicators, compares the patient against similar historical cases, and estimates whether the patient resembles patterns associated with stable outcomes or rapid deterioration. The system then assigns the patient a risk category and generates recommendation guidance that clinicians or researchers can review alongside patient data.

## AI Inputs & Outputs
Inputs: age, anaemia, diabetes, ejection fraction, serum creatinine, serum sodium, high blood pressure, smoking status, platelets, creatinine phosphokinase, sex, and historical follow-up duration (time). Outputs: adverse outcome risk probability, predicted risk category (Low/Medium/High), recommendation guidance, and top contributing risk factors.

## Intended Impact
The system aims to support earlier identification of heart failure patients whose clinical patterns resemble historical high-risk cases associated with rapid deterioration or adverse outcomes. By combining clinical indicators with historical outcome patterns, the system demonstrates how AI-assisted analytics may support monitoring prioritization, escalation consideration, and clinical decision-support workflows using real patient datasets. The project focuses on educational exploration of AI-assisted healthcare analytics rather than real-world clinical deployment.

## Weekly Progress Log
Week 1: Set up the heart failure dataset and completed data validation and cleaning. Analyzed historical outcome distribution (DEATH_EVENT) and prepared model features (X and y) for training. Generated patient_id values for patient lookup in the dashboard. Built the core prediction pipeline to generate patient risk scores and implemented the recommendation engine to provide follow-up and escalation guidance based on patient risk patterns.

Week 2: Built out the Streamlit dashboard with five core screens — an Overview Dashboard displaying KPI cards including patient count, observed mortality rate, high-risk count, and average predicted risk; a Risk Distribution chart showing patient counts across Low, Medium, and High risk categories; a Patient Review screen enabling lookup by patient ID with full prediction details, risk category, top risk factors, and recommendation output; a Model Metrics panel displaying accuracy, precision, recall, and F1-score; and a Feature Importance chart visualizing the top clinical indicators driving model predictions.