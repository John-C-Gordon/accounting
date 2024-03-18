import streamlit as st
import sqlalchemy
import pandas as pd
from datetime import datetime
# from pandasai import SmartDataframe
# from pandasai.llm import OpenAI
# from pandasai.responses.response_parser import ResponseParser
import pymysql
import mysql.connector
# from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth

#TITLE

st.set_page_config(page_icon="📊", page_title="Accounting Data Query")
# api_token = st.secrets["api_token"]
credentials = {
    "usernames":{
        "admin":{
            "name": st.secrets["USERNAME"],
            "password": st.secrets["PASSWORD"]}
        }
    }
authenticator = stauth.Authenticate(credentials, 
    "accounting_query", "abcdef", cookie_expiry_days=14)
# class StreamlitResponse(ResponseParser):
#     def __init__(self, context) -> None:
#         super().__init__(context)

#     def format_dataframe(self, result):
#         st.dataframe(result["value"])
#         return

#     def format_plot(self, result):
#         st.image(result["value"])
#         return
    
#     def format_other(self, result):
#         st.write(result["value"])
#         return
name, authentication_status, username = authenticator.login("main")

if authentication_status == False:
    st.error("Username/Password is incorrect")
if authentication_status == None:
    st.warning("Please enter Username and Password")
if authentication_status == True:
    @st.cache_resource
    def create_connection():
        connection = mysql.connector.connect(
            host = st.secrets["HOST"], # This database is hosted through AWS on my account, using the
            user = "admin",                                               # free tier
            password = st.secrets["PASSWORD"], #This password can be changed to something more secure, but wanted to ensure that the rest of the steps
                                  #would work before changing
            database = st.secrets["DB"]  # --- since the AWS service only provides a database *instance*, no database should be specified in 
                                        # this function, the database itself will be created in the following steps
        )
        return connection
    conn = create_connection()
    
    st.title('2023 Full Year Pull :clipboard:')
    
    @st.cache_data
    def get_gf():
    #     gf = pd.DataFrame(conn.query('select * from data_pull;', ttl=0))
    #     # df = pd.DataFrame(conn.query('select * from codes;', ttl=0))
    #     order_participant = pd.DataFrame(conn.query('select * from additional_fields;', ttl=0))
    #     appt_cds = pd.DataFrame(conn.query('select * from appt_codes;', ttl=0))
    #     # gf['appt_time'] = df['screening_cd']
    #     # gf['payment_uid'] = df['appointment_cd']
    #     end_date = datetime(2023, 12, 31, 0)
    #     gf['Comment_Alert'] = pd.to_datetime(gf['Comment_Alert'])
    #     gf['earned'] = gf['Comment_Alert'] < end_date
    #     gf.rename(columns={'amount_paid': 'Amount Paid', 'Comment_Alert': 'Appointment Date', 'screening_id': 'Payment Type',
    #     'earned': 'Earned'}, inplace=True)
    #     gf['Appointment Code'] = appt_cds['Appointment_Code']
    #     gf['Order GUID'] = order_participant['order_guid']
    #     gf['Participant GUID'] = order_participant['participant_guid']
    #     return gf
    # gf = get_gf()
        gf = pl.read_database("SELECT * FROM data_pull", conn)
        return gf
    gf = get_gf()
    
    st.dataframe(gf)
    
    st.header('Find row(s) by:')
    
    fields = {}
    
    col1, col2 = st.columns(2)
    with col1:
        for i in gf.columns.to_list()[0:4]:
            option = st.text_input('{}:'.format(i), key='{}'.format(i))
    with col2:
        for i in gf.columns.to_list()[4:8]:
            option = st.text_input('{}:'.format(i), key='{}'.format(i))
    
    for i in st.session_state:
        if i not in ["username", "init", "failed_login_attempts",
        "authentication_status", "name", "logout"]: # want to ignore the login session states
            if st.session_state['{}'.format(i)]:
                dict = {'{}'.format(i): str(st.session_state['{}'.format(i)])}
                fields.update(dict)
    
    # s = ""
    
    # for i in range(len(fields)):
    #     if list(fields.keys())[i] == ('Amount Paid') or list(fields.keys())[i] == ('Earned'):
    #         s += '`' + (str(list(fields.keys())[i]) + '`' + "==" + str(list(fields.values())[i]) + " &")
    #     elif list(fields.keys())[i] != (('Amount Paid') or list(fields.keys())[i] != ('Earned')):
    #         s += '`' + (str(list(fields.keys())[i])) + '`' + "==" + "'" + str(list(fields.values())[i]) + "'" + " &"
    # button1, button2, button3 = st.columns([1, 1, 1])
    # with button1:
    #     submitted = st.button('Search', type="primary")   
    
    # if len(fields) == 0:
    #     st.warning('Please enter at least one (1) of the above fields.')
    # if len(fields) != 0:
    #     if submitted:
    #         # st.write(s[:-1])
    #         st.dataframe(gf.query("{}".format(s[:-1])))
    #         st.success("{} rows returned.".format(len(gf.query("{}".format(s[:-1])).index)))

