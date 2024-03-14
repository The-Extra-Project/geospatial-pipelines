import streamlit as st
import sys
sys.path.append('.')
from vizualization_pcd  import pointcloud_vizualizer
mapping_example = pointcloud_vizualizer(storage_id="toto")
st.write(mapping_example)




