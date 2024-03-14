import streamlit as st
from pathlib import Path
import subprocess
from shutil import which
from streamlit_extras.stateful_button import button
import json
import os
import pymysql.cursors
from dotenv import load_dotenv
import time
from dotenv import load_dotenv
import re
from botocore.exceptions import ClientError
import os
load_dotenv()
import ape

st.set_page_config(
    page_title=" Circum protocol",
    layout="centered",
    initial_sidebar_state="collapsed",
)

conn = pymysql.connect(
    host="localhost",
    user="root",
    password=os.getenv("DB_PASSWD"),
    database=os.getenv("DB_DATABASE"),
    autocommit=False,
)

st.header("Circum protocol")
    
def is_tool(name):
    """Checks if a tool is installed."""
    return which(name) is not None
    
st.session_state.is_logged_in = False
st.session_state.email = None
st.session_state.space_name = None
st.session_state.db_init = False
st.session_state.account_created = True
def setup_db():
    """
    instantiates the databases in the application (for current version) in order to fetch the results of the queries.
    """
    with conn:
        if not st.session_state.db_init and not conn.query("SHOW DATABASES LIKE 'circum'"):
            conn.ping()
            with conn.cursor() as cursor:
                cursor.execute("CREATE DATABASE IF NOT EXISTS circum")
                cursor.execute("USE circum")
                cursor.execute("CREATE TABLE IF NOT EXISTS login (email VARCHAR(255), space_name VARCHAR(255),account_key VARCHAR(255) PRIMARY KEY (email))")
                cursor.execute("CREATE TABLE IF NOT EXISTS files (space_name VARCHAR(255), file_name VARCHAR(255), ipfs_key VARCHAR(128), token_minted NUMBER(128), PRIMARY KEY (space_name) )")
                st.write("setup installed")
                cursor.close()
    st.session_state.db_init = True


def account_setup():  
    st.subheader(body="login")          
    rendering_login_container = st.container(height=700, border=True)
    email = rendering_login_container.text_input("Enter your email")
    login_button = rendering_login_container.button("Login via email", key="email_login")
    if login_button:
        try:
            result = ""
            output = subprocess.check_output(["w3", "login", email])
            #rendering_login_container.write("validate the email and click on the button to then authorize the login")
            # approve =rendering_login_container.button("approve login", key="approve_login")
            # if approve:
            #     result = output.decode("utf-8")
            st.success(f"Login Successful: \n {result}")
            st.session_state.is_logged_in = True
            st.session_state.account_created = True
            st.session_state.email = email
            conn.ping()
            with conn.cursor() as cursor:
                if not cursor.execute("SELECT * FROM `login` WHERE `email`=%s", (email)):
                    cursor.execute("INSERT INTO `login`(`email`, `space_name`, `account_key`) VALUES(%s, %s, %s)", (email, space_name, "0x"))
                    cursor.close()
        except subprocess.CalledProcessError as cpe:
            st.error(f"Error running w3 login: {cpe}")
        ## NOTE: here we need to explain users about the risk of storing without recovery.
        
        current_folders = subprocess.check_output(["w3", "space", "ls"]).decode("utf-8").splitlines()
        spaces = []
        folder_name_pattern = r"(?<= )([^ ]+)$"
        for folders in current_folders:    
            match =  re.findall(folder_name_pattern, folders)
            if match:
                spaces.append(match[0])
        
        process_space_create = ""
        option_button = rendering_login_container.radio("Access storage space", options=["create new folder", "access_preexisting_folder"])
        if option_button == "create new folder":
            create_new_spaces( rendering_login_container)
        
        elif option_button == "access_preexisting_folder":
            folders_created = rendering_login_container.selectbox("select a folder to access", options=spaces)
            process_space_create = subprocess.Popen(["w3", "space" ,"add" , f"{folders_created}"], stdout=subprocess.PIPE)
        output = process_space_create.communicate()
        st.success("created the space for " + output.decode())
        st.write("setting up the session db for the user")
        ipfs_form()
                
def create_new_spaces(container: st.container):
    space_name = container.text_input("input new storage")
    st.session_state.space_name = space_name
    access_space = button("access folder", key="folder_login")
    if access_space:
        already_spaces = (subprocess.check_output(["w3", "space", "ls"]).decode()).splitlines()
        if space_name in already_spaces.decode():
            st.info("folder already exists")
            ipfs_form() 
 
    
    
    



            

def ipfs_form():
    if not st.session_state.is_logged_in:
        st.info("still not connected to web3.storage, you need to login again")
        return
    
    with st.form(key="upload_file"):
        laz_file = st.file_uploader("Upload las file (max 20GB)", type=["las", "laz", "pcd", "shp"])
        if laz_file:
            st.write("Click submit upload the file to IPFS")
        button = st.form_submit_button("Submit file for IPFS upload")
        laz_file_name = ""
        if button:
            upload_file(laz_file_name=laz_file_name)        

def upload_file(laz_file_name):
    loading_command = subprocess.Popen(["w3", "up", laz_file_name], text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = loading_command.communicate()
    if out:
        st.write(out)
        conn.ping()
        # with conn.cursor() as cursor:
        #     cursor.execute("USE circum")
        #     cursor.execute("INSERT INTO `files`(`space_name`, `file_name`, `ipfs_key`) VALUES(%s, %s, %s)", (st.session_state.space_name, laz_file_name, out.split(" ")[1]))
        #     cursor.close()
    else: 
        st.write(err)
    st.success("File uploaded successfully to IPFS!") 

def token_reimbursement_provider(storage_id="", key=""):
    # from ape import accounts, Contract
    # ## TODO: integrate the web3 wallet injection from cometh
    # token_contract = ""
    # wallet = accounts[0]
    # st.write("minting the tokens w/ wallet " + str(wallet))
    # token = Contract(address=token_contract)
    # getResultReceipt = token.getIndividualContributions(address=wallet.getAddress())
    # assert not getResultReceipt.failed, "Error getting result receipt"
    st.info(f"""💳 Account address: `{key}`    
            file uploaded: {storage_id}
            """
            )
    fetch_contributionParams = button("get contribution parameters", key="token_reimbursement")
    if fetch_contributionParams:
        while time.sleep(2):
            st.spinner(f"running chainlink function for contribution parameterx: {example_transaction_function} ")    
        example_transaction_function = "https://mumbai.polygonscan.com/tx/0xf0bbfd955d26de56e74517f9d0c42bb5edb60b78e53c8e2562c54d749da5af8b"
    #     st.info(f"""factors calculated by the curators:
    #                 actual_dataContribution: 95
    #                 recaliberation: 5
                    
    #                 txn link: 
    #                 {example_transaction_function}
                    
    #                 """, icon="🤖")
    mint_token = button("get contribution tokens ", key="mint_token")
    example_mint_values = "https://mumbai.polygonscan.com/tx/0x68e3fd3f0ac409a697f7166049bd8cf704c9c2ebec9d6d3b19b31d3631f72f0f"
    if mint_token:
        st.info(f"mint token executed: {example_mint_values}")
        st.success("getting the amount of tokens: 90 circum tokens")
def sidebar():
    st.sidebar.title("Steps")
    upload_data = st.sidebar.radio("steps", options=["Login and load data", "getting token reimbursement"])
    if upload_data == "Login and load data":
        account_setup()
    if upload_data == "getting token reimbursement":
        token_reimbursement_provider()
if __name__ == "__main__":
    setup_db()
    sidebar()