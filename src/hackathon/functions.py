import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

# For the agents
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import langchain.llms as llms
import time


def prompt_to_filter(prompt, data, OPENAI_API_KEY):
    """
    Applies a given prompt to filter a DataFrame using OpenAI's GPT model.

    Args:
    - prompt (str): A prompt describing the filter criteria for the DataFrame.
    - data (DataFrame): The DataFrame to be filtered.
    - OPENAI_API_KEY (str): The API key for OpenAI.

    Returns:
    - DataFrame: The filtered DataFrame based on the response from the OpenAI model.

    Raises:
    - ValueError: If an invalid API key is provided.
    - RuntimeError: If the maximum number of retries is reached.

    This function attempts up to 5 retries in case of transient errors.
    """
    if not OPENAI_API_KEY:
        raise ValueError("Invalid OpenAI API key provided.")

    retry_count = 0
    max_retries = 5
    wait_seconds = 2  # Time to wait between retries

    while retry_count < max_retries:
        try:
            llm = OpenAI(OPENAI_API_KEY)
            df = SmartDataframe(
                data, config={"llm": llm, "llm_model": "gpt-4-1106-preview"}
            )
            response = df.chat(prompt)
            return response
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise RuntimeError(
                    f"Maximum retry attempts reached. Last error: {str(e)}"
                )
            time.sleep(wait_seconds)


def dataframe_insights(prompt, data, OPENAI_API_KEY):
    """
    Analyzes a given DataFrame with a specific prompt using OpenAI's GPT model.

    Args:
    - prompt (str): A prompt describing the analysis or question for the DataFrame.
    - data (DataFrame): The DataFrame to analyze.
    - OPENAI_API_KEY (str): The API key for OpenAI.

    Returns:
    - str: The response from the OpenAI model.

    Raises:
    - ValueError: If an invalid API key is provided.
    - RuntimeError: If the maximum number of retries is reached.

    This function attempts up to 5 retries in case of transient errors.
    """
    if not OPENAI_API_KEY:
        raise ValueError("Invalid OpenAI API key provided.")

    retry_count = 0
    max_retries = 5
    wait_seconds = 2  # Time to wait between retries

    while retry_count < max_retries:
        try:
            agent = create_pandas_dataframe_agent(
                ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"),
                data,
                verbose=True,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                handle_parsing_errors=True,
            )
            response = agent.run(prompt)
            return response
        except Exception as e:
            retry_count += 1
            if retry_count == max_retries:
                raise RuntimeError(
                    f"Maximum retry attempts reached. Last error: {str(e)}"
                )
            time.sleep(wait_seconds)