## Clinical Problem
Heart failure patients are at risk of serious complications and mortality, but identifying high-risk patients early can be difficult when clinicians must review many clinical variables manually. Delayed identification of high-risk patients may impact timely monitoring and follow-up decisions.

## Current Workflow
Clinicians review patient vitals, lab results, and clinical history manually to assess risk. Risk assessment depends heavily on physician experience and interpretation of multiple factors such as ejection fraction, serum creatinine, sodium levels, diabetes status, and age. No AI-assisted prioritization or recommendation support is provided in the current workflow.

## Proposed AI Solution
Build a Heart Failure Risk & Outcome Recommendation System that uses machine learning to predict mortality risk based on clinical patient data. The system categorizes patients into Low, Medium, or High risk groups and generates rule-based recommendations and explainable risk insights. The system is intended for educational and decision-support demonstration purposes only and is not designed to replace clinical judgment or provide medical diagnosis.

## Workflow Integration
The AI system acts as a decision-support layer after patient clinical data is available. The model analyzes patient features, generates a risk prediction, categorizes risk level, and provides recommendation guidance that clinicians or researchers can review alongside patient data.

## AI Inputs & Outputs
Inputs: age, anaemia, diabetes, ejection fraction, serum creatinine, serum sodium, high blood pressure, smoking status, platelets, creatinine phosphokinase, sex, follow-up time. Outputs: mortality risk probability, predicted risk category (Low/Medium/High), recommendation text, and top contributing risk factors.

## Intended Impact
The system aims to improve early identification of high-risk heart failure patients, provide explainable risk insights, and demonstrate how AI can support clinical decision-support workflows using real patient datasets. The project focuses on educational exploration of AI-assisted healthcare analytics rather than real-world clinical deployment.

## Weekly Progress Log