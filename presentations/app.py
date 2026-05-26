import streamlit as st

from utils.ui_components import inject_global_css, render_sidebar
import views.overview           as overview_page
import views.patient_review     as patient_review_page
import views.model_performance  as model_performance_page
import views.feature_importance as feature_importance_page
import views.simulated_assessment as simulated_assessment_page
import views.about              as about_page

st.set_page_config(
    page_title="Heart Failure Risk Stratification",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css()
page = render_sidebar()

if   "Dashboard"    in page: overview_page.render()
elif "Patient"      in page: patient_review_page.render()
elif "Performance"  in page: model_performance_page.render()
elif "Importance"   in page: feature_importance_page.render()
elif "Simulated"    in page: simulated_assessment_page.render()
elif "About"        in page: about_page.render()