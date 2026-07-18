import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

# uv add langchain-openai

load_dotenv()

PG_CONNECTION = os.getenv("PG_CONNECTION_STRING")


def get_embeddings():
    return OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL"), dimensions=1536)


def get_vector_store(collection_name: str, pre_delete_collection: bool = False):
    return PGVector(
        collection_name=collection_name,
        connection=PG_CONNECTION,
        embeddings=get_embeddings(),
        use_jsonb=True,  # for better querying during retrieval
        pre_delete_collection=pre_delete_collection,
    )
