import sys
# sys.path.append('../')
# from vizualization_pcd import point_cloud_visualization
import numpy as np
import streamlit as st
import open3d as o3d
import time
def presenting_pointcloud(file_info:str):
    st.info("loading point cloud in plotly render , redirecting ....")
    with st.container():
        #ply_point_cloud = o3d.data.PLYPointCloud()
#         pcd = o3d.io.read_point_cloud(ply_point_cloud.path)
#         print(pcd)
#         print(np.asarray(pcd.points))
#         o3d.visualization.draw_plotly([pcd],
#                                         zoom=0.3412,
#                                         front=[0.4257, -0.2125, -0.8795],
#                                         lookat=[2.6172, 2.0475, 1.532],
#                                         up=[-0.0694, -0.9768, 0.2024])

    
# presenting_pointcloud()

