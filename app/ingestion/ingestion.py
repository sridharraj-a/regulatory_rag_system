# Load the pdf file from data folder
# extract the content
# arrive at the chunking strategy

# Load the embedding model
# embed the chunks
# connect to postgres and activate pgvector extension
# save the vector embeddings and original text in db


from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.db import get_vector_store
import tiktoken

import re
import os

load_dotenv()


def ingest_pdf(file_path):

    print("Ingestion Started")

    # 1. Load PDF file
    loader = PyPDFLoader(file_path)

    docs = loader.load()

    # 2. Clean PDF extracted text
    for doc in docs:
        doc.page_content = clean_text(doc.page_content)

    # 3. Metadata enrichment (for citation)
    for doc in docs:
        doc.metadata.update(
            {
                "source": file_path,
                "document_extension": "pdf",
                "page": doc.metadata.get("page"),
                "last_updated": os.path.getmtime(file_path),
            }
        )

    print("Before Chunking")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=100,
        length_function=token_length,
        separators=["\n\n", "\n", "Q", "Source:", " ", ""],
    )

    chunks = splitter.split_documents(docs)
    print("Total Chunks")
    print(docs[0].page_content)
    print(len(chunks))

    # 5. Generate embeddings
    # 6. Save embeddings into PGVector database

    vector_store = get_vector_store(collection_name="reg_support_desk")

    vector_store.add_documents(chunks)

    print("Ingestion Completed")


def clean_text(text: str) -> str:
    # Remove repeated whitespace/newlines
    text = re.sub(r"\s+", " ", text)

    # Remove spaces before punctuation
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)

    # Remove markdown separators
    text = re.sub(r"-{3,}", " ", text)

    # Remove duplicate spaces again
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


encoding = tiktoken.get_encoding("cl100k_base")


def token_length(text: str) -> int:
    return len(encoding.encode(text))


if __name__ == "__main__":

    ingest_pdf("app\data\Capstone_Project_1_Regulatory_Compliance_System_FAQ.pdf")
