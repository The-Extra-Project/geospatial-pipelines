import streamlit as st
import pymysql
import pandas as pd
import sys
import os
from app import conn, setup_db
from pathlib import Path
sys.path.append(os.path.join(Path(os.path.dirname(__file__)).parent.parent, '..'))

st.title("admin evaluation uploader")

def evaluation_uploader(database_connector: pymysql.connect.cursor, ipfs_key: str, user_id: any):
    st.markdown("select the user account that you want the file to be evaluated")
    
#        ## first getting the corresponding emails and their files being uploaded
 #       try:
#            conn.ping()
    all_params = conn.query("SELECT * FROM files WHERE email = %s ", (user_id,))
    st.info(f"number of files being uploaded by the user: {all_params}")
        # except pymysql.err.DatabaseError as e:
        #     st.write(e)
        # st.info(f"number of files being uploaded by the user: {all_params}")
        ## connverting the mysql result into the dataframe for display
        # df = all_params.fetchall()
        # df = pd.DataFrame(df, columns=['id', 'email','space_name', 'password', 'account_key'])
        # st.table(df)

if __name__ == "__main__":
    evaluation_uploader(database_connector=conn, ipfs_key="", user_id="malikdhruv1994@gmail.com")

