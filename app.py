import streamlit as st
from chatbot.templates.ChatbotModule import run_chatbot
from summary.templates.SummaryModule import run_summary
from predict.templates.PredictModule import run_predict

def main():
    st.set_page_config(page_title="IPO HELPER", layout="wide")

    st.title("IPO HELPER")

    st.sidebar.title("Functions")
    page = st.sidebar.selectbox("Select a page", ["Chatbot", "Summary", "Predict"])

    if page == "Chatbot":
        run_chatbot()
    elif page == "Summary":
        run_summary()
    elif page == "Predict":
        run_predict()

if __name__ == '__main__' :
    main()