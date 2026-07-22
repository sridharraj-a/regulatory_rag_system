"""
components.py

Reusable UI rendering components.
"""

from __future__ import annotations

import streamlit as st


# ---------------------------------------------------------
# User Message
# ---------------------------------------------------------
def render_user_message(message: str) -> None:
    st.markdown(message)


# ---------------------------------------------------------
# Assistant Response
# ---------------------------------------------------------
def render_assistant_response(answer: dict) -> None:
    """
    Render QueryResponse.
    """

    # -------------------------------
    # Answer
    # -------------------------------

    st.markdown(answer.get("answer", ""))

    st.divider()

    # -------------------------------
    # Confidence
    # -------------------------------

    confidence = float(answer.get("confidence_score", 0))

    col1, col2 = st.columns([5, 1])

    with col1:

        st.caption("Confidence")

        st.progress(confidence)

    with col2:

        st.metric(
            label="Confidence",
            value=f"{confidence:.0%}",
            label_visibility="collapsed",
        )

    # -------------------------------
    # Summary
    # -------------------------------

    rule_summary = answer.get(
        "rule_summary",
        [],
    )

    if rule_summary:

        with st.expander(
            "📋 Rule Summary",
            expanded=False,
        ):

            for item in rule_summary:

                st.markdown(f"- {item}")

    # -------------------------------
    # Sources
    # -------------------------------

    citations = answer.get(
        "citations",
        [],
    )

    if citations:

        with st.expander(
            "📚 Sources",
            expanded=False,
        ):

            for index, citation in enumerate(
                citations,
                start=1,
            ):

                st.markdown(f"### Source {index}")

                st.write(
                    "**Document:**",
                    citation.get(
                        "source",
                        "-",
                    ),
                )

                if citation.get("page"):

                    st.write(
                        "**Page:**",
                        citation["page"],
                    )

                if citation.get("section"):

                    st.write(
                        "**Section:**",
                        citation["section"],
                    )

                if citation.get("excerpt"):

                    st.info(citation["excerpt"])

                st.divider()

    # -------------------------------
    # Disclaimer
    # -------------------------------

    disclaimer = answer.get("disclaimer")

    if disclaimer:

        with st.expander(
            "⚠ Regulatory Disclaimer",
            expanded=False,
        ):

            st.write(disclaimer)


# ---------------------------------------------------------
# Developer Details
# ---------------------------------------------------------
def render_developer_details(
    retrieval: dict,
) -> None:

    documents = retrieval.get(
        "documents",
        [],
    )

    with st.expander(
        "🛠 Developer Details",
        expanded=False,
    ):

        st.write(
            "**Retrieval Strategy:**",
            retrieval.get(
                "retrieval_strategy",
                "-",
            ),
        )

        st.write(
            "**Retrieved Chunks:**",
            len(documents),
        )

        if not documents:

            st.info("No retrieved documents.")

            return

        st.divider()

        for i, document in enumerate(
            documents,
            start=1,
        ):

            metadata = document.get(
                "metadata",
                {},
            )

            st.markdown(f"### Chunk {i}")

            left, right = st.columns(2)

            with left:

                st.write(
                    "**Score:**",
                    document.get(
                        "retrieval_score",
                        "-",
                    ),
                )

                st.write(
                    "**Score Type:**",
                    document.get(
                        "score_type",
                        "-",
                    ),
                )

            with right:

                st.write(
                    "**Page:**",
                    metadata.get(
                        "page_label",
                        metadata.get(
                            "page",
                            "-",
                        ),
                    ),
                )

                st.write(
                    "**Document:**",
                    metadata.get(
                        "title",
                        metadata.get(
                            "source",
                            "-",
                        ),
                    ),
                )

            with st.expander(
                "Metadata",
                expanded=False,
            ):

                st.json(metadata)

            st.code(
                document.get(
                    "content",
                    "",
                ),
                language="text",
            )

            st.divider()


# ---------------------------------------------------------
# Upload Result
# ---------------------------------------------------------
def render_upload_result(
    result: dict,
) -> None:

    st.success(
        result.get(
            "message",
            "Document uploaded successfully.",
        )
    )

    with st.container(border=True):

        st.markdown(f"**📄 File**  \n" f"{result.get('file_name', '-')}")

        st.markdown(f"**📂 Location**  \n" f"`{result.get('location', '-')}`")


# ---------------------------------------------------------
# Error
# ---------------------------------------------------------
def render_error(
    message: str,
) -> None:

    st.error(message)


# ---------------------------------------------------------
# Technical Error
# ---------------------------------------------------------
def render_technical_error(
    error: str,
) -> None:

    with st.expander(
        "Technical Details",
        expanded=False,
    ):

        st.code(error)
