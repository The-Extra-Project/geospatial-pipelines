import streamlit as st
from utils.email_reseand import headers, html
import os
from pathlib import Path
def upload_file_modal(container: st.container, city):
    while container.empty():
        uploader_area = st.container(height=100)
        container.write(f"<h4>upload data on {city} map </h4>", unsafe_allow_html=True)
        with uploader_area:         
            st.image(os.path.join(Path(__file__).parent.parent, "assets/upload_files.png"), width=200)
            st.write("<h5>browse your compatible pointcloud (.laz,.shp), video (mp4,360 standard) and images (jpg...) for uploading</h5>", unsafe_allow_html=True)
            st.file_uploader("upload via transferring file", type=["laz", "pcd", "jpg", "mp4"])
        
        next_steps= st.container(height=30)
        while next_steps.empty():
            st.write("after uploading, you will receive the notification detailing the reward you received within a week") 



upload_file_modal(container=st.container(height=350, border=True), city="helsinki")
