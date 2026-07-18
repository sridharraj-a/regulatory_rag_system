Regulatory Compliance RAG Chatbot
# uv init
# python -m venv .venv    or    uv venv 
# .venv\Scripts\activate.bat
# uv add python-dotenv 
# uv add langchain_community 
# uv add langchain
# uv add pypdf
# uv run app/ingestion/ingestion.py
# --- uv run python -m app.ingestion.ingestion.py
# uv add langchain-openai
# uv add langchain_postgres
# uv add fastapi 
# uv add fastapi uvicorn
# uv run uvicorn app.main:app --reload

To access fastapi swagger end point use http://127.0.0.1:8000/docs

# uv add streamlit requests
# streamlit run app/ui/app.py