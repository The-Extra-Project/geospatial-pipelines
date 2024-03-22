import streamlit as st
import os
import pymysql
import sys
from streamlit_extras.stateful_button import button
import subprocess
from sqlalchemy import text
from pymysql.err import MySQLError
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from scripts.uploader import upload_file_modal
from utils.email_reseand import email_params, headers, html

conn = st.connection(name="circum", type="sql")
st.session_state.db_init = False

st.session_state.signup = False



def setup_db():
    """
    Instantiates the databases in the application (for current version) in order to fetch the results of the queries.
    """
    try:    
        query_setup = "USE login"
        create_table = "CREATE TABLE IF NOT EXISTS `login` (`email` VARCHAR(60),  `space_name` varchar(128), `password` varchar(256), `account_key` VARCHAR(256), PRIMARY KEY (email) ) "
        conn.query(create_table)
        conn.query(query_setup)

    except MySQLError as e:
        st.error(f"Error creating database: {e}")
    

def signup(container: any):
    setup_db()
    email = container.text_input("enter your registeration email", type="default")
    password_input = container.text_input("enter your password", type="password")
    password_confirm = container.text_input("confirm your password", type="password")
    signup_button = container.button("Signup", key="signup_button")
    if not st.session_state.db_init and password_input == password_confirm:
        st.info("creating account")
        demo_details = ['documents','0xdemo']
        
        
        # query_insert = f"INSERT INTO `login` (`email`, `space_name`, `password`, `account_key`)  VALUES ('{email}', '{demo_details[0]}', '{password_input}', '{demo_details[1]}')"
        # ##INSERT INTO `login` (`email`, `space_name`, `password`, `account_key`)  VALUES ('{email}', {demo_details[0]}, {password_input}, {demo_details[1]})
        # conn.query()
        # conn.query(query_insert)
        # container.success("account created, now setting up the storage space in web3.storage")
        # st.session_state.signup = True
        # conn.close()
        # st.session_state.db_init = True
        # create_new_spaces(container, demo_details[0])
        
    email_params(email, headers[0], html[0])
    upload_file_modal(container,"helsinki")
    
        

def create_new_spaces(space_name, container):
    with container.empty():
        st.session_state.space_name = space_name
        already_spaces = (subprocess.check_output(["w3", "space", "ls"])).splitlines()
        st.session_state.already_spaces = already_spaces
        if space_name in already_spaces:
            st.info("folder already exists, retry again") 
            st.info(st.session_state.already_spaces)
        else:
            process_space_create = subprocess.Popen(["w3", "space" ,"add" , f"{space_name}"], stdout=subprocess.PIPE)
            output = process_space_create.communicate()
            st.success("created the space for " + str(output))
            
# if __name__ == "__main__":
#     container = st.container(height=400)
#     setup_db()
#     signup(container)
#     create_new_spaces("", container)
