import json

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from graph import NewsGraph
from tools import search_bbc, search_guardian

load_dotenv()

with open("config.json") as f:
    config = json.load(f)

# Initialize the language model
if config["provider"] == "azure":
    llm = AzureChatOpenAI(
        deployment_name=config["model"],
        temperature=config["temperature"],
    )
elif config["provider"] == "openai":
    llm = ChatOpenAI(
        model=config["model"],
        temperature=config["temperature"],
    )
else:
    raise ValueError(f"Provider {config['provider']} not supported.")

tools = [search_bbc, search_guardian]
llm_with_tools = llm.bind_tools(tools)

# # Initialize the Streamlit app
st.title("News Chatbot")

if "graph" not in st.session_state:
    st.session_state.graph = NewsGraph(llm_with_tools, tools)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Message News Chatbot"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.session_state.graph.invoke({"user_prompt": prompt})
        st.write(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
