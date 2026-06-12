# HeartGuard — AI-Assisted Heart Failure Risk Stratification & Recommendation System
Educational clinical decision-support system that uses machine learning and explainable healthcare analytics to identify patients whose clinical patterns resemble historical higher-risk heart failure cases.


## Description
HeartGuard is a machine learning-based healthcare analytics application designed to analyze historical heart failure patient data and estimate adverse outcome risk using clinical indicators such as ejection fraction, serum creatinine, sodium levels, diabetes status, and age.  
The system generates risk predictions, explainable insights, and rule-based recommendation guidance to demonstrate how AI-assisted analytics may support monitoring prioritization and clinical review workflows.


## Problem Statement
Heart failure patients may experience rapid clinical deterioration, but identifying high-risk patients early can be difficult when clinicians must manually evaluate multiple clinical indicators and historical patterns.  
Traditional assessment workflows rely heavily on physician interpretation and may not systematically leverage historical outcome data to support prioritization and monitoring decisions.


## Solution Overview
The system uses supervised machine learning to analyze patient clinical indicators and compare them against historical outcome patterns associated with elevated heart failure risk.  
Based on prediction results, the application:
- estimates adverse outcome probability
- assigns Low, Medium, or High risk categories
- generates recommendation guidance
- highlights top contributing clinical risk factors


## System Workflow / ML Pipeline
1. Load and preprocess historical heart failure dataset
2. Clean and validate clinical features
3. Train classification model using supervised learning
4. Generate risk probability predictions
5. Categorize patients into risk groups
6. Produce explainable prediction insights
7. Display results through an interactive Streamlit dashboard


## Key Features
- AI-assisted heart failure risk prediction
- Low / Medium / High patient risk categorization
- Explainable prediction insights using feature importance
- Rule-based clinical recommendation guidance
- Interactive Streamlit dashboard interface
- Historical outcome pattern analysis
- Clinical feature visualization and monitoring support


## Results / Model Performance
The system was evaluated using historical heart failure clinical records and standard classification metrics.  
Evaluation outputs include:
- Accuracy
- Precision
- Recall
- F1-score
- Prediction probability analysis
- Feature importance ranking

Key contributing risk factors identified by the model include:
- ejection fraction
- serum creatinine
- serum sodium
- age


## Tech Stack
| Layer | Technologies |
| -------- | -------- |
| Programming | Python |
| Machine Learning | Scikit-learn |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib |
| UI Framework | Streamlit |
| Model Serialization | Pickle |
| Development Tools | Jupyter Notebook, Git |


## Architecture Diagram
The system architecture consists of:
- clinical dataset ingestion
- preprocessing pipeline
- machine learning prediction engine
- explainability layer
- recommendation generation module
- Streamlit dashboard interface

The workflow demonstrates how AI-assisted analytics can integrate into clinical decision-support scenarios using historical patient data.


## Clinical Features / Data Dictionary
The model uses demographic, laboratory, cardiovascular, and comorbidity-related clinical indicators including:
- age
- anaemia
- diabetes
- ejection fraction
- serum creatinine
- serum sodium
- platelets
- smoking status
- high blood pressure
- follow-up duration

Detailed field definitions and application-generated outputs are documented in `docs/data_dictionary.md`.


## Demo / How To Use
1. Launch the [Streamlit application](https://clinical-workflow-ai-general-project-atllz5s7tcbgndqqmb7fwy.streamlit.app/)
2. Navigate to the Simulated Assessment page
3. Enter patient clinical indicators
4. Review generated risk probability and category
5. Analyze recommendation guidance and contributing risk factors

The application demonstrates how clinical indicators may be analyzed using machine learning-assisted healthcare analytics workflows


## Screenshots
TBA


## Repository Structure
TBA


## Setup Instructions
```
# Clone repository
git clone <repository-url>

# Install dependencies
pip install -r requirements.txt

# Run Streamlit application
streamlit run presentations/app.py
```


## Challenges & Lessons Learned
Key challenges encountered during development included:
- selecting clinically meaningful features
- balancing model simplicity and interpretability
- designing explainable prediction outputs
- translating prediction probabilities into understandable risk categories

The project also highlighted the importance of transparency and explainability in healthcare AI workflows.


## Disclaimer
This project is intended for educational and research demonstration purposes only.  
The generated predictions, recommendations, and explainability outputs are not intended for medical diagnosis, treatment decisions, or replacement of professional clinical judgment.
