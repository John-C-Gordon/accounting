import streamlit as st
import sqlalchemy
from datetime import datetime
import mysql.connector
import polars as pl
import pymysql
import pandas as pd

st.title("Test")
@st.cache_resource
def create_connection():
    connection = mysql.connector.connect(
        host = st.secrets["HOST"], # This database is hosted through AWS on my account, using the
        user = "admin",                                               # free tier
        password = st.secrets["PASSWORD"], #This password can be changed to something more secure, but wanted to ensure that the rest of the steps
                              #would work before changing
        database = st.secrets["DB"],  # --- since the AWS service only provides a database *instance*, no database should be specified in 
                                    # this function, the database itself will be created in the following steps
        buffered = True
    )
    return connection
conn = create_connection()
cursor = conn.cursor()
# @st.cache_data
# def get_gf():
#     gf = pl.read_database("SELECT * FROM appt_codes;", conn)
#     return gf
# gf = get_gf()
cursor.execute('''
SELECT * FROM data_pull''')
connection.commit()
st.write(cursor)
# st.dataframe(gf)
