import streamlit as st
from pathlib import Path
import subprocess
from shutil import which
from streamlit_extras.stateful_button import button
import os
import pymysql.cursors


st.set_page_config(
    page_title="🗺️ Extra[labs] circum platform",
    layout="centered",
    initial_sidebar_state="collapsed",
)


from dotenv import load_dotenv
import time
from dotenv import load_dotenv
import re
import os
from web3_integration import wallet_login
from utils.email_reseand import email_params, headers, html
from streamlit.connections import SQLConnection
from scripts.signup import signup




load_dotenv()

# conn = pymysql.connect(
#     host="localhost",
#     user="root",
#     password=os.getenv("DB_PASSWD"),
#     database=os.getenv("DB_DATABASE"),
#     autocommit=False,
# )

conn = st.connection(name="circum", type="sql")
def create_new_spaces(container: st.container, name):
    space_name = container.text_input("input new storage")
    st.session_state.space_name = space_name
    access_space = button("access folder", key="folder_login")
    if access_space:
        already_spaces = (subprocess.check_output(["w3", "space", "ls"]).decode()).splitlines()
        if space_name in already_spaces.decode():
            st.info("folder already exists, retry again") 
        else:
            process_space_create = subprocess.Popen(["w3", "space" ,"add" , f"{name}"], stdout=subprocess.PIPE)
            output = process_space_create.communicate()
            st.success("created the space for " + output.decode())
            st.write("setting up the session db for the user")


col,icon1, icon2 = st.columns(3)
width_icon = 100
height_icon = 100

col.empty()
with icon1:
    st.image("./assets/extra_logo.png", width=width_icon)

with icon2:
    st.image("./assets/FVH_logo_black_thumb.png", width=width_icon+50)
col.empty()   


def authenticate_passwrd(email: str, password:str):
    if not conn.query("SELECT * FROM login WHERE email = %s , password = %s", (email, password)):
        st.write(f"password or email is incorrect")
    st.session_state.is_logged_in = True
    st.session_state.email = email
    return True


def wallet_description():
    pass


def is_tool(name):
    """Checks if a tool is installed."""
    return which(name) is not None
    
st.session_state.is_logged_in = False
st.session_state.email = None
st.session_state.space_name = None
st.session_state.db_init = False
st.session_state.account_created = True

## connectors to the database (considering the fact that these databases are being instantiated)
st.session_state.db_access = ""
st.session_state.db_init = True
# def setup_db():
#     """
#     Instantiates the databases in the application (for current version) in order to fetch the results of the queries.
#     """
#     st.session_state.db_init = True



def account_setup(container):  
    email = container.text_input("Enter your email")
    password = container.text_input("Enter your password", type="password")
    col1, col2, col3 = st.columns([.5,.7,.5])
    login_button = col2.button("Login via email/password", key="email_login")
    #forgot_password =  col3.button("forgot password")
    if login_button:
        container.empty()
        #create_wallet(rendering_login_container)
        try:
            login_object = authenticate_passwrd(email=email, password=password)
            st.success(f"Login Successful")
            container.empty()
            st.session_state.is_logged_in = True
            st.session_state.account_created = True
            st.session_state.email = email
            storage_space = st.radio("select the storage space", options=["create new folder", "access_preexisting_folder"])
            
            conn.query("SELECT * FROM `login` WHERE `email`=%s", (email))
            conn.query("INSERT INTO `login`(`email`, `space_name`, `account_key`) VALUES(%s, %s, %s)", (email, storage_space, ""))
        except subprocess.CalledProcessError as cpe:
            st.error(f"Error running w3 login: {cpe}")
        
        current_folders = subprocess.check_output(["w3", "space", "ls"]).decode("utf-8").splitlines()
        
        spaces = []
        folder_name_pattern = r"(?<= )([^ ]+)$"
        for folders in current_folders:    
            match =  re.findall(folder_name_pattern, folders)
            if match:
                spaces.append(match[0])
        
        process_space_create = ""
        option_button = container.radio("Access storage space", options=["create new folder", "access_preexisting_folder"])
        if option_button == "create new folder":
            create_new_spaces(container)
        
        elif option_button == "access_preexisting_folder":
            folders_created = container.selectbox("select a folder to access", options=spaces)
            process_space_create = subprocess.Popen(["w3", "space" ,"add" , f"{folders_created}"], stdout=subprocess.PIPE)
        output = process_space_create.communicate()
        st.success("created the space for " + output.decode())
        st.write("setting up the session db for the user")
        #ipfs_form()
                
# def ipfs_form(container):

#     while container.empty():
#         if not st.session_state.is_logged_in:
#             st.info("still not connected to web3.storage, you need to login again")
#             return
        
#         with st.form(key="upload_file"):
#             laz_file = st.file_uploader("Upload las file (max 20GB)", type=["las", "laz", "pcd", "shp"])
#             if laz_file:
#                 st.write("Click submit upload the file to IPFS")
#             button = st.form_submit_button("Submit file for IPFS upload")
#             laz_file_name = ""
#             if button:
#                 upload_file(laz_file_name=laz_file_name)        

def upload_file(laz_file_name):
    loading_command = subprocess.Popen(["w3", "up", laz_file_name], text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = loading_command.communicate()
    if out:
        st.write(out)
        ##conn.ping()
        # with conn.cursor() as cursor:
        #     cursor.execute("USE circum")
        #     cursor.execute("INSERT INTO `files`(`space_name`, `file_name`, `ipfs_key`) VALUES(%s, %s, %s)", (st.session_state.space_name, laz_file_name, out.split(" ")[1]))
        #     cursor.close()
    else: 
        st.write(err)
    st.success("File uploaded successfully to IPFS!, sending the details about renumeration once its finalised") 
 
def token_reimbursement_provider(storage_id="", key=""):
   pass


def sidebar():
    st.markdown("<h4 style='text-align: center; color: black;'> Welcome to the project CIRCUM uplaoder</h4> ", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center; color: black;'> We build better 3D maps by remunerating companies and citizens for their data contributions. Find out more <a link='https://www.extralabs.xyz'> here </a> </h5>",unsafe_allow_html=True)  
    rendering_login_container = st.container(height=350, border=True)
    account_setup(rendering_login_container)
    st.markdown("<a style='text-align: right; color: black;' href='https://localhost:8501/forgot' > Forgot the password </a>", unsafe_allow_html=True)
    st.button(" Signup", on_click=signup, args=(rendering_login_container,))

if __name__ == "__main__":
    
    
    sidebar()