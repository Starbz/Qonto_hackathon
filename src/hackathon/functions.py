import pandas as pd
import numpy as np
import hackathon.prompts as prompts
from dotenv import load_dotenv
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
import os
import math
from flask import Flask, request, jsonify

# For the agents
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import langchain.llms as llms
import time
import json

#For the main OPENAI ASSISTANT
import openai as openai


#ENVIRONMENT VARIABLES
load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def create_temporal_features(df, date_column):
    """
    Adds temporal features to the DataFrame.

    Parameters:
    df (DataFrame): The input DataFrame with a date or datetime column.
    date_column (str): The name of the column containing the date or datetime.

    Returns:
    DataFrame: The original DataFrame with additional columns for temporal features.
    """

    # Ensure the date column is in datetime format
    df[date_column] = pd.to_datetime(df[date_column])

    # Day of the week (0 = Monday, 6 = Sunday)
    df["day_of_week"] = df[date_column].dt.dayofweek

    # Day of the year
    df["day_of_year"] = df[date_column].dt.dayofyear

    # Week of the year
    df["week_of_year"] = df[date_column].dt.isocalendar().week

    # Week of the month
    df["week_of_month"] = df[date_column].apply(lambda x: math.ceil(x.day / 7.0))

    # Weekday (1 if it's a weekday, 0 if it's a weekend)
    df["is_weekday"] = df[date_column].dt.weekday < 5

    # Month
    df["month"] = df[date_column].dt.month

    # Year
    df["year"] = df[date_column].dt.year

    return df


def prompt_to_filter(prompt, data_to_filter):
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
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

    retry_count = 0
    max_retries = 5
    wait_seconds = 2  # Time to wait between retries
    data = create_temporal_features(data_to_filter.reset_index(drop = True), "date")
    while retry_count < max_retries:
        try:
            llm = OpenAI(OPENAI_API_KEY)
            df = SmartDataframe(
                data, config={"llm": llm, "llm_model": "gpt-3.5-turbo-0613"}
            )
            response = df.chat(prompt).convert_dtypes()
            return response
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                print("Error: Maximum number of retries reached.")
                return pd.DataFrame()
            time.sleep(wait_seconds)


def dataframe_insights(prompt, data_to_filter):
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

    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
    retry_count = 0
    max_retries = 5
    wait_seconds = 2  # Time to wait between retries

    data = create_temporal_features(data_to_filter.reset_index(drop = True), "date")

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
                return pd.DataFrame()
            time.sleep(wait_seconds)

# Create or load assistant
def create_assistant(client):
    assistant_file_path = "/Users/arthur.cruiziat/dev/Qonto_hackathon/src/hackathon/assistant.json"

    # Load existing assistant if file exists
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, "r") as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data["assistant_id"]
            print("Loaded existing assistant ID.")
    else:
        print("Creating a new assistant...")
        # Create a new assistant if file does not exist
        assistant = client.beta.assistants.create(
            instructions=prompts.assistant_instructions,
            model="gpt-4-1106-preview",
            tools=[
                # {"type": "retrieval"},
                {
                    "type": "function",
                    "function": {
                        "name": "prompt_to_filter",
                        "description": "Applies a given prompt to filter the transaction dataframe from the user.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "prompt": {
                                    "type": "string",
                                    "description": "A prompt describing the filter criteria for the DataFrame.",
                                },
                                "data_filtered": {
                                    "type": "string",
                                    "description": "The transaction dataframe to be filtered",
                                },
                            },
                            "required": ["prompt"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "dataframe_insights",
                        "description": "Given a prompt, analyzes the transaction dataframe and outputs insights.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "prompt": {
                                    "type": "string",
                                    "description": "A prompt describing the analysis or question for the DataFrame.",
                                },
                                "data_filtered": {
                                    "type": "string",
                                    "description": "The transaction dataframe to analyse",
                                },
                            },
                            "required": ["prompt"],
                        },
                    },
                },
            ],
            # file_ids=[file.id],
        )

        # Save assistant ID to file for future runs
        with open(assistant_file_path, "w") as file:
            json.dump({"assistant_id": assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id

def start_conversation(client):
    """
    Starts a new conversation and creates a new thread.

    This function initiates a new conversation by creating a new thread using the client's beta API. 
    It prints a message indicating that a new conversation is starting, and another message displaying 
    the newly created thread's ID.

    Returns:
        dict: A dictionary containing the ID of the newly created thread.
    """
    print("Starting a new conversation...")
    thread = client.beta.threads.create()
    print(f"New thread created with ID: {thread.id}")
    return {"thread_id": thread.id}


def chat(client, thread_id, user_input, data_filtered, assistant_id):
    """
    Handles chat interactions within a specified thread.

    This function processes user input in a chat conversation. It first checks if the thread ID is provided,
    then adds the user's message to the chat thread and runs the assistant. If the assistant's response
    requires action, such as calling specific functions ('dataframe_insights' or 'prompt_to_filter'), it
    handles these calls and submits the outputs back to the thread. The function continues to check the
    status of the assistant's run and handles actions as required. Finally, it retrieves the assistant's
    response and returns it along with the filtered data.

    Parameters:
    thread_id (str): The ID of the thread in which the chat is happening.
    user_input (str): The input message from the user.
    data_filterered (DataFrame): The DataFrame that is possibly used for filtering or analysis.

    Returns:
    dict: A dictionary containing the assistant's response and the filtered DataFrame.

    Note: This function assumes that the 'client' and 'assistant_id' variables are already defined
    and accessible in its scope.
    """

    if not thread_id:
        print("Error: Missing thread_id")

    print(f"Received message: {user_input} for thread ID: {thread_id}")

    # Add the user's message to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_input
    )

    # Run the Assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id, assistant_id=assistant_id
    )

    # Check if the Run requires action (function call)
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id, run_id=run.id
        )
        # print(f"Run status: {run_status.status}")
        if run_status.status == "completed":
            break
        elif run_status.status == "requires_action":
            # Initialize a dictionary to store outputs for each tool call
            tool_outputs = []

            # Handle the function calls
            print(len(run_status.required_action.submit_tool_outputs.tool_calls))
            for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
                arguments = json.loads(tool_call.function.arguments)
                print(arguments["prompt"])

                output = None
                if tool_call.function.name == "dataframe_insights":
                    output = dataframe_insights(arguments["prompt"], data_filtered)
                elif tool_call.function.name == "prompt_to_filter":
                    output = prompt_to_filter(arguments["prompt"], data_filtered)
                    final_filtered_dataframe = output  # Update the final DataFrame

                # Add the output to the tool_outputs list
                if output is not None:
                    if isinstance(output, pd.DataFrame):
                        # Convert DataFrame to a JSON string
                        output_json = output.to_json(orient='records')
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": output_json
                        })
                    else:
                        # For other data types, just convert to string
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": str(output)
                        })

            # Submit all tool outputs at once
            if tool_outputs:
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            time.sleep(1)  # Wait for a second before checking again

    # Retrieve and return the latest message from the assistant
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value

    print(f"Assistant response: {response}")
    return {"response": response, "data_filterered": final_filtered_dataframe}