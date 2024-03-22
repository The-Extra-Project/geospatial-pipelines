import streamlit as st
import requests 


st.set_page_config(
    page_title="process compute state",
    layout="centered"   
)

def process_compute_dashboard():
    with st.container() as compute_container:
        process_name, details , time_compute  = st.columns(3)
        process_name = st.header("process name")
        details = st.header("details of the compute job")
        time_compute = st.header("time remaining for compute")
        
        
        