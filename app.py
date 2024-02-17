
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components
from pyecharts.charts import Bar, Pie
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from pandasai.responses.response_parser import ResponseParser
import os

st.set_page_config(page_icon="📊", page_title="Accounting Data Query")

conn = st.connection("gsheets", type=GSheetsConnection)
api_token = st.secrets["api_token"]

data = conn.read(worksheet='merged_filtered')

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
st.title('2023 Full Year Pull')
data['Participant_GUID'] = data['customer_uid']
data['Order_GUID'] = data['order_guid']

st.dataframe(data)

# f = (
#     Pie(init_opts=opts.InitOpts(theme=ThemeType.DARK))
#     .add(
#         "Payment Type",
#         [list(z) for z in zip(data.groupby(['payment_type_id']).sum().index.tolist(), data.groupby(['payment_type_id']).sum()['amount_paid'].tolist())],
#         # rosetype="radius",
#         label_opts=opts.LabelOpts(is_show=True),
#     )
#     .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: ${c}"))
#     .render_embed()
# )
# g = (
#     Pie(init_opts=opts.InitOpts(theme=ThemeType.DARK))
#     .add(
#         "Earned",
#         [list(z) for z in zip(data.groupby(['Earned']).sum().index.tolist(), data.groupby(['Earned']).sum()['amount_paid'].tolist())],
#         # rosetype="radius",
#         label_opts=opts.LabelOpts(is_show=True),
#     )
#     .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: ${c}"))
#     .render_embed()
# )
# components.html(f, width=1500, height=550, scrolling=True)
# components.html(g, width=1500, height=550, scrolling=True)
query = st.text_area('What query would you like to run?')

if query:
    openai_llm = OpenAI(api_token = api_token)
    sdf = SmartDataframe(data, config={'llm': openai_llm, "response_parser": StreamlitResponse})
    
    sdf.chat(query)
    # st.write(answer)


