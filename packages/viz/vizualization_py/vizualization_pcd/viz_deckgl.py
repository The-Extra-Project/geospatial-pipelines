import streamlit as st
import sys

from vizualization_py.vizualization_pcd  import pointcloud_vizualizer
mapping_example = pointcloud_vizualizer(storage_id="toto")
st.write(mapping_example)




