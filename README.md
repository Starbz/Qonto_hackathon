# Qonto Hackathon Project: AI-Driven Chatbot for Transaction Insights
## What's the Feature?
Our chatbot empowers users to interact with their Qonto transaction data via natural language prompts, offering capabilities such as:
- Filtering transactions based on user queries.
- Providing a quick summary of filtered transactions, including total and average amounts.
- Delivering further insights on non-filter queries, like identifying the highest spending team in a specific month.

## Why Build It?
Despite existing transaction filters on Qonto, their complexity can hinder user experience, especially for intricate queries. Our chatbot simplifies this process, enhancing user interaction with their financial data by making it easy to obtain transaction summaries and insights through simple conversational prompts.

## Why Should Qonto Invest?
This feature, while not groundbreaking, is an accessible step towards more sophisticated conversational AI applications within Qonto, potentially leading to the development of more complex functions such as card creation, user additions, and making transactions.

# Technical details

We embarked on a project with the goal of transforming the banking experience. Our aim was to allow users to engage with their transaction data through **natural language queries**, leveraging AI to provide both data filtering and analytical insights. This one-day project serves as a foundation, demonstrating the potential for more extensive development in the future.

**Key Components of Our Project:**

1. **AI Agent Integration**:
    - *Our Approach*: We integrated an AI agent into the banking system, positioning it as the main interface for users to interact with their transaction data. Utilizing the OpenAI Beta Assistant API, this agent is capable of understanding and responding to various user queries.
    - **Using OpenAI Beta Assistant API**: We developed the AI agent with this API, enabling the creation of a system that can interpret user queries and interact with specific banking functionalities.
    - **Data Access Control**: Our design ensures the AI agent accesses only the data relevant to each individual user, maintaining strict privacy and security standards.
2. **Functional Capabilities**:
    - *Our Strategy*: We designed specific functions that empower the AI agent to interact effectively with transaction data. These functions are essential for executing data filtering and providing analytics in response to user requests.
    - **Data Filtering Function**: This function allows the AI agent to process and filter transaction data according to user queries.
    - **Analytics Function**: This enables the AI agent to conduct statistical analysis and offer insightful data interpretations.
3. **Operational Logic**:
    - *Our Implementation*: To ensure the AI agent uses the right function for each user query, we established specific prompting logic. This is crucial for the agent to operate intelligently and context-aware.
    - **Function Invocation**: The AI agent is programmed to use specific prompts to decide the most appropriate function to execute based on the user's query.
4. **Current Limitations and Path Forward**:
    - *Our Reflection*: Recognizing the constraints of this initial one-day build, we see numerous opportunities for improvement and expansion.
    - **API Limitations**: Given the beta status of the OpenAI Assistant API, there are limitations such as potential delays in response and user queuing during peak times.
    - **Prospects for Custom AI Agent Development**: We see a significant opportunity to develop custom AI agents using more advanced platforms like Mistral medium or GPT-4, aiming for enhanced performance and capabilities.

This initial project lays the groundwork for a more sophisticated and robust system. By addressing current limitations and exploring advanced AI solutions, we envision a future where banking becomes more interactive, personalized, and user-friendly through AI integration.


## Future Directions:
Acknowledging the project's initial scope, we aim to address current API limitations and explore advanced AI platforms for improved performance, envisioning a banking experience that's more interactive and personalized through AI.
