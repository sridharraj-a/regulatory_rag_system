import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/api/v1/query"

st.set_page_config(page_title="Regulatory RAG Assistant", page_icon="🏦", layout="wide")

st.title("🏦 Banking Regulatory Assistant")

# ---------------------------------------------------
# Initialize chat history
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------
# Display previous conversation
# ---------------------------------------------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            st.subheader("Summary")

            for rule in message["rule_summary"]:
                st.write(f"• {rule}")

            confidence = message["confidence_score"]

            st.subheader("Confidence")

            col1, col2 = st.columns([4, 1])

            with col1:
                st.progress(confidence)

            with col2:
                st.write(f"{confidence:.0%}")

            with st.expander("Sources"):

                for citation in message["citations"]:

                    st.markdown(f"**📄 Document:** {citation['source']}")

                    st.markdown(f"**📑 Page:** {citation['page']}")

                    st.markdown(f"**📚 Section:** {citation['section']}")

                    st.markdown("**Excerpt:**")

                    st.info(citation["excerpt"])

                    st.divider()
            with st.expander("⚠️ Regulatory Disclaimer"):

                st.info(message["disclaimer"])


# ---------------------------------------------------
# Chat input
# ---------------------------------------------------
prompt = st.chat_input("Ask a banking regulation question...")

if prompt:

    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Call FastAPI
    with st.chat_message("assistant"):

        with st.spinner("Searching regulations..."):

            response = requests.post(API_URL, json={"query": prompt})

        if response.status_code != 200:
            st.error(response.text)
            st.stop()

        result = response.json()

        st.markdown(result["answer"])

        st.subheader("Summary")

        for rule in result["rule_summary"]:
            st.write(f"• {rule}")

        confidence = result["confidence_score"]

        st.subheader("Confidence")

        col1, col2 = st.columns([4, 1])

        with col1:
            st.progress(confidence)

        with col2:
            st.write(f"{confidence:.0%}")

        with st.expander("Sources"):

            for citation in result["citations"]:

                st.markdown(f"**📄 Document:** {citation['source']}")

                st.markdown(f"**📑 Page:** {citation['page']}")

                st.markdown(f"**📚 Section:** {citation['section']}")

                st.markdown("**Excerpt:**")

                st.info(citation["excerpt"])

                st.divider()
        with st.expander("⚠️ Regulatory Disclaimer"):

            st.info(result["disclaimer"])

    # Save assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "rule_summary": result["rule_summary"],
            "confidence_score": result["confidence_score"],
            "citations": result["citations"],
            "disclaimer": result["disclaimer"],
        }
    )
