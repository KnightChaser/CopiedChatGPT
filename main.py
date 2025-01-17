import streamlit as st
from langchain_core.messages.chat import ChatMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from dotenv import load_dotenv
from typing import Any
import yaml

# Retrieve the environment variables
load_dotenv()

st.title("CCGPT(Copied ChatGPT)")

# Add a sidebar button to clear the chat
with st.sidebar:
    clear_button = st.button("Clear chat")
    if clear_button:
        st.session_state["messages"] = []
    selected_prompt = st.selectbox(
        "Select the prompt type",
        ("Basic mode", "Blog post", "Tweet"),
        index=0
    )

# Initialize the session state(messages) and display the messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

def print_messages() -> None:
    """
    Print the messages in the chat
    """
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)

def add_message(role: str, message: str) -> None:
    """
    Add a message to the chat
    """
    st.session_state["messages"].append(ChatMessage(role=role, content=message))

def load_prompt_from_yaml(file_path: str) -> ChatPromptTemplate:
    """
    Load a ChatPromptTemplate from a YAML file
    """
    with open(file_path, 'r') as file:
        prompt_data = yaml.safe_load(file)
    template = ChatPromptTemplate.from_messages(
        [(message['role'], message['content']) for message in prompt_data['messages']]
    )
    return template

def create_langchain(prompt_type) -> Any:
    """
    Generate a LCEL chain for the assistant
    """
    if prompt_type == "Basic mode":
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful and kind assistant. Answer the question succinctly and informatively."),
                ("user", "#Question:\n{question}"),
            ]
        )
    elif prompt_type == "Blog post":
        prompt = hub.pull("hardkothari/blog-generator")
    elif prompt_type == "Tweet":
        prompt = load_prompt_from_yaml('tweet_prompt.yml')
    else:
        raise ValueError("Invalid prompt type")
    
    llm = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0
    )

    chain = prompt | llm | StrOutputParser()
    return chain

print_messages()
user_input = st.chat_input("Say what you are wondering about...")
if user_input:
    st.chat_message("user").write(user_input)
    chain = create_langchain(selected_prompt)
    if selected_prompt == "Blog post":
        response = chain.stream({"text": user_input, "target_audience": "general user"})
    elif selected_prompt == "Tweet":
        response = chain.stream({"text": user_input})
    elif selected_prompt == "Basic mode":
        response = chain.stream({"question": user_input})
    with st.chat_message("assistant"):
        # Stream the response token, in an empty container
        container = st.empty()
        accumulated_response = ""
        st.markdown(f"### {selected_prompt} mode")
        for token in response:
            accumulated_response += token
            container.markdown(accumulated_response)

    # Save the messages
    add_message("user", user_input)
    add_message("assistant", f"{selected_prompt} mode\n\n{accumulated_response}")
