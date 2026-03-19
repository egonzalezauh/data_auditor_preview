import streamlit as st
from src.data_loader import load_csv
from src.analysis import perform_individual_analysis
from src.join_simulator import run_join_simulator
from src.recommendations import run_recommendations_engine

st.set_page_config(page_title="Data Auditor Pro", layout="wide")

st.title("Data Auditor Pro")

tab1, = st.tabs([
    "Análisis Individual"
])

if 'df_a' not in st.session_state:
    st.session_state.df_a = None

with tab1:
    st.header("Análisis de Tabla Principal (Tabla A)")
    file_a = st.file_uploader("Sube tu archivo CSV principal (Tabla A)", type=["csv"], key="file_a")
    if file_a:
        st.session_state.df_a = load_csv(file_a)
        if st.session_state.df_a is not None:
            perform_individual_analysis(st.session_state.df_a, file_a.name)

