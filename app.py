import streamlit as st
import pandas as pd
import altair as alt
from dotenv import load_dotenv
from langchain.agents import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
import hackathon.functions as f
from hackathon.prompts import *
import openai as openai
import os


load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
trx_path = os.environ["trx_df_path"]


# App title
st.set_page_config(page_title="🚀 Transaction Filter")
st.title("🚀 Get a better understanding of your transactions")

@st.cache_data
def get_data():
    df = pd.read_csv(trx_path)
    df['date'] = pd.to_datetime(df['date'])
    return df.set_index("user")

client = openai.OpenAI(api_key=OPENAI_API_KEY)
assistant_id = f.create_assistant(client)
thread = f.start_conversation(client)


df = get_data()



# Using "with" notation
with st.sidebar:
    st.title('💬 Transaction App 101')
    user = st.selectbox(
        "For which user would you like to see data?",
        df.index.unique().tolist(),
        index=None,
        placeholder="Select user ...",
        )
    st.write('You selected:', user)

def clear_filters():
    st.session_state.data_displayed = st.session_state.data_init.copy()
    del st.session_state['messages']
    del st.session_state['data_displayed']
st.sidebar.button('Clear Filters', on_click=clear_filters)



# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]




prompt = st.chat_input("Enter your request :")

if not user:
    st.error("Please select at least one user.")
else:
    st.session_state.data_init = df.loc[user].reset_index(drop=True)
    if "data_displayed" not in st.session_state.keys():
        st.session_state.data_displayed = st.session_state.data_init.copy()
    if prompt:
        response = f.chat(client, thread_id = thread['thread_id'], user_input = prompt, data_filterered = st.session_state.data_displayed, assistant_id=assistant_id)
        st.session_state.data_displayed = response['data_filterered']
        st.session_state.messages.append({"role": "assistant", "content": response['response']})    
        with st.chat_message('user'):
            st.write(prompt)

    message = st.session_state.messages[-1]
    with st.chat_message(message["role"]):
        st.write(message["content"])
    
    st.write("### Transactions (€)", st.session_state.data_displayed.sort_values(by = 'date').reset_index(drop=True))

