import streamlit as st
from model.Chatbot.ChatModel import Chat
from streamlit_chat import message

# def run_chatbot():
#     st.subheader("챗봇 서비스")

#     # Initialize chat history
#     if "messages" not in st.session_state:
#         st.session_state.messages = []

#     # Display chat messages from history on app rerun
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

#     # Accept user input
#     if prompt := st.chat_input("Please enter the question"):
#         # Display user message in chat message container
#         with st.chat_message("user"):
#             st.markdown(prompt)
#         # Add user message to chat history
#         st.session_state.messages.append({"role": "user", "content": prompt})

#         # Display assistant response in chat message container
#         with st.chat_message("assistant"):
#             result = Chat().flare.run(prompt)
#             response = "".join(result)
#             st.markdown(response)
#         # Add assistant response to chat history
#         st.session_state.messages.append({"role": "assistant", "content": response})

def run_flare():
    st.subheader("_Enhances responses by using real-time web search results_ :red[Flare Chat] 🔥")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            message(msg["content"], is_user=True, key=f"user_{i}")  # 사용자 메시지에 고유 key 추가
        else:
            message(msg["content"], key=f"bot_{i}")  # 챗봇 메시지에 고유 key 추가

    # Accept user input using st.chat_input, which places the input box at the bottom
    if prompt := st.chat_input("Please enter your question"):
        # Display user message
        message(prompt, is_user=True, key=f"user_input")
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response
        result = Chat().flare.run(prompt)
        response = "".join(result)
        message(response, key=f"bot_response")
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})