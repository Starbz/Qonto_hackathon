import streamlit as st
import pandas as pd
import altair as alt
from dotenv import load_dotenv
from langchain.agents import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
import os


load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
trx_path = os.environ["trx_df_path"]


# App title
st.set_page_config(page_title="🚀 Transaction Filter")
st.title("🚀 Get a better understanding of your transactions")

@st.cache_data
def get_UN_data():
    df = pd.read_csv(trx_path)
    df['date'] = pd.to_datetime(df['date'])
    return df.set_index("user")

def start_conversation():
    thread = {'thead_id': 'thread_3ROE0kjAGABFuOVMzLdL0N7d'}
    return thread

def chat(thread_id, user_input, data_filterered):
    if "year_filter" not in st.session_state.keys():
        st.session_state.year_filter = [int(user_input)]
    else:
        st.session_state.year_filter.append(int(user_input))

    response = 'We filtered your data on the following years: '+', '.join(map(str, st.session_state.year_filter))+'. Would you like to add another year?'
    filtered_dataframe = data_filterered[data_filterered['date'].dt.year.isin(st.session_state.year_filter)]

    return {"response": response, "data_filterered": filtered_dataframe}

df = get_UN_data()



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
    del st.session_state['year_filter']
    del st.session_state['data_displayed']
st.sidebar.button('Clear Filters', on_click=clear_filters)



# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "You don't have any year filters yet, would you like to specify a year?"}]




prompt = st.chat_input("Enter a year :")

if not user:
    st.error("Please select at least one user.")
else:
    st.session_state.data_init = df.loc[user]
    if "data_displayed" not in st.session_state.keys():
        st.session_state.data_displayed = st.session_state.data_init.copy()
    if prompt:
        response = chat(start_conversation(), prompt, st.session_state.data_init)
        st.session_state.data_displayed = response['data_filterered']
        st.session_state.messages.append({"role": "assistant", "content": response['response']})    
    # Display or clear chat messages
    message = st.session_state.messages[-1]
    with st.chat_message(message["role"]):
        st.write(message["content"])
    
    st.write("### Transactions (€)", st.session_state.data_displayed.sort_values(by = 'date').reset_index(drop=True))

