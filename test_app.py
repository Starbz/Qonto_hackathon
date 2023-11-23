import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from pandasai.responses.streamlit_response import StreamlitResponse

# Create dataframes
employees_df = pd.DataFrame(
    {
        "EmployeeID": [1, 2, 3, 4, 5],
        "Name": ["John", "Emma", "Liam", "Olivia", "William"],
        "Department": ["HR", "Sales", "IT", "Marketing", "Finance"],
        "Salary": [5000, 6000, 4500, 7000, 5500],
    }
)

# Initialize LLM and SmartDatalake
llm = OpenAI()
dl = SmartDataframe(
    employees_df,
    config={"llm": llm, "verbose": True, "response_parser": StreamlitResponse},
)

# Streamlit app
def main():
    st.title("PandasAI Charts in Streamlit")
    st.write("## Employee Salaries")
    response = dl.chat("Filter the data to show only employees with salary > 5000")
    st.pyplot(response.get_plot())

if __name__ == "__main__":
    main()
