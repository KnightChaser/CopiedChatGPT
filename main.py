import streamlit as st
from langchain_core.messages.chat import ChatMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from dotenv import load_dotenv
from typing import Any

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
        ("Basic mode", "Blog post", "Abbreviation"),
        index = 0
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
    st.session_state["messages"].append(ChatMessage(role=role,
                                                    content=message))

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
    elif prompt_type == "Abbreviation":
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a writing expert. Read the following article and summarize it without losing the main idea."),
                ("user", "#Article:\n{question}"),
            ]
        )
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
    else:
        response = chain.stream({"question": user_input})
    with st.chat_message("assistant"):
        # Stream the response token, in an empty container
        container = st.empty()
        accumulated_response = ""
        for token in response:
            accumulated_response += token
            container.markdown(accumulated_response)

    # Save the messages
    add_message("user", user_input)
    add_message("assistant", response)