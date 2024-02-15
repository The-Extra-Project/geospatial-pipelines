import streamlit as st
from pathlib import Path
import subprocess
from shutil import which
from streamlit_extras.stateful_button import button

st.set_page_config(
    page_title="Circum protocol",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.header("Circum protocol steps")


def set_button_state(button):
    """Maintains the state value of the result of the various functions that generate the result"""
    st.session_state.clicked[button] = True

def is_tool(name):
    """Checks if a tool is installed."""
    return which(name) is not None


def upload_file():
    if not is_tool("w3"):
        st.error("Requires installation of the @web3-storage/w3cli. Installing now...")
        with st.spinner("Installing w3cli..."):
            subprocess.check_call(["npm", "install", "-g", "@web3-storage/w3cli"])

    upload_method = st.selectbox("Upload method", options=["Lighthouse", "Web3 Storage"])

    if upload_method == "Lighthouse":
        # TODO: Implement Lighthouse upload
        st.warning("Lighthouse upload not yet implemented")

    elif upload_method == "Web3 Storage":
        email = st.text_input("Enter your email")
        if button("Login via email", key="email login"):
            try:
                output = subprocess.check_output(["w3", "login", email])
                st.write(output.decode())
                st.session_state.is_logged_in = True
                st.session_state.email = email
                #st.rerun()
            except subprocess.CalledProcessError as cpe:
                st.error(f"Error running w3 login: {cpe}")
    
            ipfs_form()
                
            
            

            

def login_params(email):
    
    dataplaceholder = st.empty()
    ipfs_form(dataplaceholder)


def ipfs_form():
    if not st.session_state.is_logged_in:
        st.info("still not connected to web3.storage, you need to login again")
        return
    result = st.container()
    email = st.session_state.email
    with st.form(key="upload_file"):
        laz_file_name = st.text_input("Enter file path (supported enviornments : las, laz,pcd, shp)")
        laz_file = st.file_uploader("Upload las file (max 20GB)", type=["las", "laz", "pcd", "shp"])

        if laz_file:
            st.write("Click submit to get the IPFS CID")

        if st.form_submit_button("Submit file for IPFS upload"):
            loading_command = subprocess.Popen(["w3", "up", laz_file_name], text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            out, err = loading_command.communicate()
            with result.container():
                st.write(out)
            st.write("File uploaded successfully to IPFS!")


def sidebar():
    st.sidebar.title("Steps")
    upload_data = st.sidebar.checkbox("Upload data")
    if upload_data:
        upload_file()

    # TODO: Implement data preparation pipeline
    st.sidebar.checkbox("Run data preparation pipeline")


def main():
    sidebar()


if __name__ == "__main__":
    main()
