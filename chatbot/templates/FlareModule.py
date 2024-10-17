import streamlit as st
from model.Chatbot.ChatModel import Chat
from streamlit_chat import message

def run_flare():
    st.subheader("_Enhances responses by using real-time web search results_ :red[Flare Chat] 🔥")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            message(msg["content"], is_user=True, key=f"user_{i}")  
        elif msg["role"] == "assistant":
            message(msg["content"], key=f"bot_{i}") 

    if prompt := st.chat_input("Please enter your question"):
        message(prompt, is_user=True, key=f"user_input")

        st.session_state.messages.append({"role": "user", "content": prompt})

        result = Chat().flare.run(prompt)
        response = "".join(result)
        message(response, key=f"bot_response")

        st.session_state.messages.append({"role": "assistant", "content": response})