"""
sidebar.py

Renders the application sidebar.
"""

from __future__ import annotations

import streamlit as st

from api import (
    check_api_health,
    get_api_version,
    upload_pdf,
)
from components import (
    render_error,
    render_technical_error,
    render_upload_result,
)


def render_sidebar() -> bool:
    """
    Renders the sidebar.

    Returns
    -------
    bool
        True if Developer Mode is enabled.
    """

    with st.sidebar:

        st.title("🏦 Regulatory Assistant")

        st.caption("Version 1.0")

        st.divider()

        # ---------------------------------------------------
        # API Status
        # ---------------------------------------------------

        connected = check_api_health()

        if connected:
            st.success("🟢 API Connected")
        else:
            st.error("🔴 API Offline")

        st.caption(f"Backend Version: {get_api_version()}")

        st.divider()

        # ---------------------------------------------------
        # Developer Mode
        # ---------------------------------------------------

        developer_mode = st.toggle(
            "Developer Mode",
            value=False,
            help="Shows retrieval diagnostics and enables document upload.",
        )

        # ---------------------------------------------------
        # Developer Section
        # ---------------------------------------------------

        if developer_mode:

            st.markdown("### 🛠 Developer Tools")

            uploaded_file = st.file_uploader(
                "Choose a PDF",
                type=["pdf"],
            )

            if uploaded_file:

                st.info(f"Selected: **{uploaded_file.name}**")

                if st.button(
                    "Upload & Ingest",
                    use_container_width=True,
                ):

                    with st.spinner("Uploading document..."):

                        result, error = upload_pdf(uploaded_file)

                    if error:

                        render_error("Upload failed.")
                        render_technical_error(error)

                    else:

                        render_upload_result(result)

        st.divider()

        # ---------------------------------------------------
        # Conversation Controls
        # ---------------------------------------------------

        st.markdown("### 💬 Conversation")

        if st.button(
            "🗑 Clear Conversation",
            use_container_width=True,
        ):

            st.session_state.messages = []

            st.rerun()

        st.divider()

        # ---------------------------------------------------
        # About
        # ---------------------------------------------------

        with st.expander("About"):

            st.markdown("""
This application answers banking regulatory questions
using Retrieval-Augmented Generation (RAG).

The answers are generated exclusively from uploaded
regulatory documents.
                """)

    return developer_mode
