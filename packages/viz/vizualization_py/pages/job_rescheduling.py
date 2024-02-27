import streamlit as st
import requests
import os
import uuid
import leafmap.foliumap as leafmap
#from  data_preparation.data_preparation.cropping import CroppingUtilsSHP
#import vizualization_py.visualization as viz
base_url = "https://localhost:3000/"


def run_data_preparation_pipeline():
    st.write("select the algorithm and the file that you want to run")
    algorithm_category = st.selectbox("Select the algorithm", options=["SR", "Neuralangelo"])
        

def reconstruction_dashboard():
    st.title("circum:- scheduling compute job")
    
    with st.container():
        Map = leafmap.Map(layers_control = True)
        
    with st.container(height=300,border=True):
        
        choice = st.selectbox("select the option",("via 3D coordinates","via 2D coordinates"))
        if choice == "via 2D coordinates":
            st.write("enter the point of interest (in WGS 84 standard)")
            X_coord = st.number_input("X coordinate", min_value=1)
            Y_coord = st.number_input("Y coordinate", min_value=1)
            
        

reconstruction_dashboard()