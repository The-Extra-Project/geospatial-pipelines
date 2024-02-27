import streamlit as st
from pathlib import Path
import subprocess
from shutil import which
from streamlit_extras.stateful_button import button
import os

st.set_page_config(
    page_title="Circum protocol",
    layout="wide",
    initial_sidebar_state="expanded",
)


conn = st.connection("mysql", type='streamlit.connections.sql_connection.SQLConnection')

st.header("Circum protocol")
    
def is_tool(name):
    """Checks if a tool is installed."""
    return which(name) is not None
    
st.session_state.is_logged_in = False
st.session_state.email = None
st.session_state.space_name = None
st.session_state.db_init = False
with conn.cursor():
    conn.query("CREATE DATABASE IF NOT EXISTS circum")
    conn.query("USE circum")
    table_login = conn.query("CREATE TABLE IF NOT EXISTS login (email VARCHAR(255), space_name VARCHAR(255), PRIMARY KEY (email))")

def account_setup():            
    email = st.text_input("Enter your email")
    space_name = st.text_input("folder name")
    if button("Login via email", key="email_login"):
        try:
            output = subprocess.check_output(["w3", "login", email])
            st.write(output.decode())
            st.session_state.is_logged_in = True
            st.session_state.email = email
            st.session_state.space_name = space_name
            st.write("test: checking the parameter of db instantiation:" + str(table_login.columns))
            with table_login.cursor() as cursor:
                cursor.execute('sql',"INSERT INTO login VALUES(" + email + ", " +  space_name + ")")   
        except subprocess.CalledProcessError as cpe:
            st.error(f"Error running w3 login: {cpe}")
        ## NOTE: here we need to explain users about the risk of storing without recovery.
        already_spaces = subprocess.check_output(["w3", "space", "ls"])
        if space_name in already_spaces.decode():
            st.write("folder already exists, upload your data to it")
            ipfs_form() 
            exit(1)          

        process_space_create = subprocess.Popen(["w3", "space" ,"create" , "--no-recovery",  f"{space_name}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process_space_create.communicate()
        st.success("created the space for " + output.decode())
        st.write("setting up the session db for the user")
        
            ## now the key is revealed to user 

        ## fetch the keys from the spaces command and then fetch the given keys 
        ## then store the keys in the.env file
        ipfs_form()
                
            
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
            st.write("Click submit upload the file to IPFS")
        button = st.form_submit_button("Submit file for IPFS upload")
        
        if button:
            upload_file(laz_file_name=laz_file_name)        

def upload_file(laz_file_name):
    loading_command = subprocess.Popen(["w3", "up", laz_file_name], text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = loading_command.communicate()
    if out:
        st.write(out)
    else: 
        st.write(err)
    st.success("File uploaded successfully to IPFS!")



def sidebar():
    st.sidebar.title("Steps")
    upload_data = st.sidebar.radio("steps", options=["Login with account", "loading_data", "getting token reimbursement"])
    if upload_data == "Login with account":
        account_setup()
    

def main():
    sidebar()

if __name__ == "__main__":
    main()
