import os
import re

import tiktoken
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.db import get_vector_store
from app.core.logger import logger

# Load environment variables
load_dotenv()


# Initialize tokenizer
try:
    encoding = tiktoken.get_encoding("cl100k_base")
except Exception:
    encoding = None


def token_length(text: str) -> int:
    """
    Returns token count for a given text.
    Falls back to character count if tokenizer is unavailable.
    """
    if encoding is None:
        return len(text)

    return len(encoding.encode(text))


def clean_text(text: str) -> str:
    """
    Cleans extracted PDF text.
    """

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    text = re.sub(r"-{3,}", " ", text)
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


def ingest_pdf(file_path: str) -> None:
    """
    Reads a PDF, creates chunks, generates embeddings,
    and stores them in PGVector.
    """

    try:

        logger.info("========== INGESTION STARTED ==========")

        # -------------------------------------------------
        # Validate file
        # -------------------------------------------------

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF not found: {file_path}")

        if not file_path.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported.")

        logger.info("Loading PDF...")

        loader = PyPDFLoader(file_path)

        docs = loader.load()

        if not docs:
            raise ValueError("PDF contains no readable content.")

        logger.info("Loaded %s pages.", len(docs))

        # -------------------------------------------------
        # Clean extracted text
        # -------------------------------------------------

        logger.info("Cleaning extracted text...")

        for doc in docs:
            doc.page_content = clean_text(doc.page_content)

        # -------------------------------------------------
        # Metadata
        # -------------------------------------------------

        logger.info("Adding metadata...")

        last_updated = os.path.getmtime(file_path)

        for doc in docs:
            doc.metadata.update(
                {
                    "source": file_path,
                    "document_extension": "pdf",
                    "page": doc.metadata.get("page"),
                    "last_updated": last_updated,
                }
            )

        # -------------------------------------------------
        # Chunking
        # -------------------------------------------------

        logger.info("Chunking document...")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=60,
            length_function=token_length,
            separators=[
                "\n\n",
                "\n",
                "Q",
                "Source:",
                " ",
                "",
            ],
        )

        chunks = splitter.split_documents(docs)

        if not chunks:
            raise ValueError("Chunking failed. No chunks were created.")

        logger.info(
            "Total chunks created: %s",
            len(chunks),
        )

        # -------------------------------------------------
        # Store embeddings
        # -------------------------------------------------

        logger.info("Connecting to PGVector...")

        vector_store = get_vector_store(collection_name="reg_support_desk")

        logger.info("Saving embeddings...")

        vector_store.add_documents(chunks)

        logger.info(
            "Successfully indexed %s chunks.",
            len(chunks),
        )

        logger.info("========== INGESTION COMPLETED ==========")

    except FileNotFoundError as e:

        logger.error(str(e))
        raise

    except ValueError as e:

        logger.error(str(e))
        raise

    except Exception as e:

        logger.exception("Unexpected error during ingestion.")

        raise RuntimeError(f"PDF ingestion failed: {str(e)}") from e


if __name__ == "__main__":

    try:

        ingest_pdf(r"app\data\Capstone_Project_1_Regulatory_Compliance_System_FAQ.pdf")

    except Exception as e:

        logger.error("Application failed: %s", str(e))
