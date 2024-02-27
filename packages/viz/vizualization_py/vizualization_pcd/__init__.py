import os
import streamlit as st

import streamlit.components.v1  as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = False
pointcloud_framework = ''
_custom_dataframe = ''
if not _RELEASE:
    _custom_dataframe = components.declare_component(
        "custom_dataframe",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    pointcloud_framework = components.declare_component("custom_dataframe", path=build_dir)

def pointcloud_vizualizer(storage_id, key=None):
    return pointcloud_framework(storage_id=storage_id, key=key, default=os.path.join(os.getcwd() ,"frontend/example_assets"))

