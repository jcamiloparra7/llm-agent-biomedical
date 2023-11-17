# Import required libraries
import os

import streamlit as st
from medical_assistant import assistant

NBCI_LOGO_PATH = os.getenv("NBCI_LOGO_PATH")
INTRODUCTION_TEXT_PATH = os.getenv("INTRODUCTION_TEXT_PATH")


def main():
    st.set_page_config(
        page_title="NBCI Medical Assistant",
        page_icon="🤖",
        initial_sidebar_state="expanded",
    )

    with open(NBCI_LOGO_PATH) as nbci_logo:
        svg = nbci_logo.read()

    with open(INTRODUCTION_TEXT_PATH) as introduction_md:
        introduction_text = introduction_md.read()

    with st.sidebar:
        # st.image(image=nbci_logo)
        st.markdown(svg, unsafe_allow_html=True)
        st.markdown(introduction_text)

    st.header(
        "🤖: Greetings! I'm designed to retrieve medical information 📚 and"
        "  answer your questions."
    )

    medical_assistant = assistant.MedicalAssistant()

    if "chat_history_user" not in st.session_state:
        st.session_state["chat_history_user"] = []
        st.session_state["chat_history_assistant"] = []

    user_input = st.chat_input("Enter your request")

    if user_input:
        with st.spinner(f"Retrieving information for: {user_input}..."):
            response = medical_assistant.answer_query(user_input)

        # Add the bot response and user input to the chat history
        st.session_state["chat_history_user"].append(user_input)
        st.session_state["chat_history_assistant"].append(response)

        # Display the chat history in order
        for i in range(len(st.session_state["chat_history_user"])):
            user_message = st.session_state["chat_history_user"][i]
            assistant_message = st.session_state["chat_history_assistant"][i]

            with st.chat_message("user"):
                st.write(user_message)
            with st.chat_message("assistant"):
                st.write(assistant_message)


if __name__ == "__main__":
    main()
