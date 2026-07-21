import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

from app.core.logger import logger

load_dotenv()

PG_CONNECTION = os.getenv("PG_CONNECTION_STRING")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")


def get_embeddings() -> OpenAIEmbeddings:
    """
    Initialize and return the OpenAI embedding model.
    """

    try:
        if not EMBEDDING_MODEL:
            raise ValueError("EMBEDDING_MODEL is missing in the .env file.")

        logger.info("Loading embedding model...")

        embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            dimensions=1536,
        )

        logger.info("Embedding model loaded successfully.")

        return embeddings

    except Exception as e:
        logger.exception("Failed to initialize embedding model.")
        raise RuntimeError(f"Embedding initialization failed: {str(e)}") from e


def get_vector_store(
    collection_name: str,
    pre_delete_collection: bool = False,
) -> PGVector:
    """
    Initialize and return PGVector vector store.
    """

    try:
        if not PG_CONNECTION:
            raise ValueError("PG_CONNECTION_STRING is missing in the .env file.")

        logger.info(
            "Connecting to PGVector collection: %s",
            collection_name,
        )

        vector_store = PGVector(
            collection_name=collection_name,
            connection=PG_CONNECTION,
            embeddings=get_embeddings(),
            use_jsonb=True,
            pre_delete_collection=pre_delete_collection,
        )

        logger.info("Connected to PGVector successfully.")

        return vector_store

    except Exception as e:
        logger.exception("Failed to initialize PGVector.")

        raise RuntimeError(f"Database connection failed: {str(e)}") from e
