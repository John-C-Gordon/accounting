import streamlit as st
import sqlalchemy
import pandas as pd
from datetime import datetime
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from pandasai.responses.response_parser import ResponseParser
import pymysql

#TITLE

st.set_page_config(page_icon="📊", page_title="Accounting Data Query")
api_token = st.secrets["api_token"]

class StreamlitResponse(ResponseParser):
    def __init__(self, context) -> None:
        super().__init__(context)

    def format_dataframe(self, result):
        st.dataframe(result["value"])
        return

    def format_plot(self, result):
        st.image(result["value"])
        return
    
    def format_other(self, result):
        st.write(result["value"])
        return


@st.cache(allow_output_mutation=True)
def load_data():
    name='mysql' 
    type='sql'
    return st.connection(name=name,type=type)
conn = load_data()

st.title('2023 Full Year Pull')

gf = pd.DataFrame(conn.query('select * from data_pull;', ttl=0))
df = pd.DataFrame(conn.query('select * from codes;', ttl=0))
gf['appt_time'] = df['screening_cd']
gf['payment_uid'] = df['appointment_cd']

end_date = datetime(2023, 12, 31, 0)
gf['Comment_Alert'] = pd.to_datetime(gf['Comment_Alert'])
gf['earned'] = gf['Comment_Alert'] < end_date

gf.rename(columns={'amount_paid': 'Amount Paid', 'Comment_Alert': 'Appointment Date', 'screening_id': 'Payment Type', 
                   'payment_type_id': 'Payment UID', 'appt_time': 'Screening Code', 'payment_uid': 'Appoitment Code', 'screening_cd': 'Screening ID'}, inplace=True)
st.dataframe(gf)

query = st.text_area('What query would you like to run?')

if query:
    openai_llm = OpenAI(api_token = api_token)
    sdf = SmartDataframe(gf, config={'llm': openai_llm, "response_parser": StreamlitResponse})
    
    sdf.chat(query)
    # st.write(answer)

# st.write(gf.groupby(['earned']).sum()['amount_paid'])
