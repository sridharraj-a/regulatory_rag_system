import streamlit as st

from api import query_api
from components import (
    render_user_message,
    render_assistant_response,
    render_developer_details,
)
from sidebar import render_sidebar
from styles import apply_styles

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Banking Regulatory Assistant",
    page_icon="🏦",
    layout="wide",
)

apply_styles()

st.title("🏦 Banking Regulatory Assistant")

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
developer_mode = render_sidebar()

# --------------------------------------------------
# Session State
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------
# Display Conversation History
# --------------------------------------------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message["role"] == "user":

            render_user_message(message["content"])

        else:

            render_assistant_response(message["response"]["query_response"])

            if developer_mode:
                render_developer_details(message["response"]["retrieval"])

# --------------------------------------------------
# Chat Input
# --------------------------------------------------
prompt = st.chat_input("Ask a banking regulation question...")

if prompt:

    # ----------------------------------------------
    # Save & Display User Message
    # ----------------------------------------------
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        render_user_message(prompt)

    # ----------------------------------------------
    # Assistant Response
    # ----------------------------------------------
    with st.chat_message("assistant"):

        with st.spinner("Searching regulatory documents..."):

            result, error = query_api(prompt)

        if error:

            st.error("Unable to process your request.")

            with st.expander("Technical Details"):
                st.code(error)

            st.stop()

        render_assistant_response(result["query_response"])

        if developer_mode:
            render_developer_details(result["retrieval"])

    # ----------------------------------------------
    # Save Assistant Response
    # ----------------------------------------------
    st.session_state.messages.append(
        {
            "role": "assistant",
            "response": result,
        }
    )
