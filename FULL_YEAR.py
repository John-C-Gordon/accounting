import streamlit as st
import sqlalchemy
import pandas as pd
from datetime import datetime
# from pandasai import SmartDataframe
# from pandasai.llm import OpenAI
# from pandasai.responses.response_parser import ResponseParser
import pymysql
import mysql.connector
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
import polars as pl
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType
from pyecharts import options as opts
from streamlit_echarts import st_pyecharts
import streamlit.components.v1 as components
from pyecharts.globals import ThemeType

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
    # selected = option_menu(menu_title=None, options=['Analysis', 'Search', 'Smart Query'], icons=['clipboard2-data', 'search', 'magic'], orientation='horizontal',)
    @st.cache_resource
    def load_data():
        name='mysql' 
        type='sql'
        return st.connection(name=name,type=type)
    conn = load_data()
    
    st.title('2023 Full Year Pull :clipboard:')
    
    @st.cache_data
    def get_gf():
        gf = pl.DataFrame(conn.query('select * from data_pull;', ttl=0))
        # participant_guid = conn.query('select participant_guid from additional_fields;', ttl=0)
        # order_guid = conn.query('select order_guid from additional_fields;', ttl=0)
        # appt_codes = conn.query('select * from appt_codes;', ttl=0)
        # gf.insert_column(5, pl.Series(participant_guid["participant_guid"]))
        # gf.insert_column(6, pl.Series(order_guid["order_guid"]))
        gf = gf.with_columns(pl.col('Appointment Date').str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S", strict=False).cast(pl.Datetime))
        end_date = datetime(2023, 12, 31, 0)
        gf = gf.with_columns(pl.when(pl.col("Appointment Date") < end_date).then(True).otherwise(False).alias("Earned"))
        return gf
    gf = get_gf()

    
    selected = option_menu(menu_title=None, options=['Analysis', 'Search', 'Smart Query'], \
                           icons=['clipboard2-data', 'search', 'magic'], orientation='horizontal', key='Menu') 
    # st.write(selected)
    if selected == 'Search':
    
        st.header('Find row(s) by:')
        
        fields = {}
        
        col1, col2 = st.columns(2)
        with col1:
            for i in gf.columns[2:4]:
                option = st.text_input('{}:'.format(i), key='{}'.format(i))
            
            option = st.text_input('Amount Paid:', key='Amount Paid')
        with col2:
            for i in gf.columns[4:8]:
                option = st.text_input('{}:'.format(i), key='{}'.format(i))
        
        for i in st.session_state:
            if i not in ["username", "init", "failed_login_attempts",
            "authentication_status", "name", "logout", "Menu"]: # want to ignore the login session states
                if st.session_state['{}'.format(i)]:
                    dict = {'{}'.format(i): str(st.session_state['{}'.format(i)])}
                    fields.update(dict)
        
        s = ""
        
        for i in range(len(fields)):
            if list(fields.keys())[i] == ('Amount Paid') or list(fields.keys())[i] == ('Earned'):
                s += '`' + (str(list(fields.keys())[i]) + '`' + "==" + str(list(fields.values())[i]) + " AND")
            elif list(fields.keys())[i] != (('Amount Paid') or list(fields.keys())[i] != ('Earned')):
                s += '`' + (str(list(fields.keys())[i])) + '`' + "==" + "'" + str(list(fields.values())[i]) + "'" + " AND"
        button1, button2, button3 = st.columns([1, 1, 1])
        with button1:
            submitted = st.button('Search', type="primary")   
        
        ctx = pl.SQLContext(data=gf)
        
        if len(fields) == 0:
            st.warning('Please enter at least one (1) of the above fields.')
        if len(fields) != 0:
            if submitted:
                st.dataframe(ctx.execute('''SELECT * FROM data WHERE {}'''.format(s[:-3]), eager=True))
                
    if selected == 'Analysis':
        earned_unearned = (gf.group_by("Earned").agg(pl.col("Amount Paid").sum().alias("Total Revenue")))
#col1, col2, col3 = st.columns(3)
            
        # with col1:
        st.dataframe(earned_unearned)
        payment_types = gf.group_by("Payment Type").agg(pl.col("Amount Paid").sum().alias("Total Revenue"))
        c = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.CHALK))
            .add_xaxis(
                payment_types['Payment Type'].to_list())
            .add_yaxis("Revenue ($)", payment_types['Total Revenue'].to_list())
            # .add_yaxis("商家B", [20, 10, 40, 30, 40, 50])
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-30), is_scale=True),
                title_opts=opts.TitleOpts(title="Revenue by Payment Type")
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="${c}"))
            .render_embed()
        )
        with st.container():
            components.html(c, width=1100, height=550, scrolling=True)

