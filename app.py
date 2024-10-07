import streamlit as st
from chatbot.templates.FlareModule import run_flare
from chatbot.templates.DocsBasedModule import run_docs_based
from summary.templates.SummaryModule import run_summary
from predict.templates.PredictModule import run_predict

def main():
    st.set_page_config(page_title="IPO HELPER", layout="wide")

    st.title("IPO HELPER")

    st.sidebar.title("Functions")
    
    tabs = st.sidebar.selectbox("Select a page", ["Chatbot", "Summary", "Predict"])

    if tabs == "Chatbot":
        chatbot_tab = st.sidebar.radio("Select a Chatbot mode", ["Flare Chatbot", "Document Based Chatbot"])
        if chatbot_tab == "Flare Chatbot":
            run_flare()
        elif chatbot_tab == "Document Based Chatbot":
            run_docs_based()
    
    elif tabs == "Summary":
        run_summary()
    
    elif tabs == "Predict":
        run_predict()

if __name__ == '__main__':
    main()