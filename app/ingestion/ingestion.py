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
from core.db import get_vector_store

import re
import os


load_dotenv()


def clean_text(text):

    text = text.replace("\r", " ")

    # Replace multiple newlines with one
    text = re.sub(r"\n{2,}", "\n", text)

    # Replace tabs
    text = re.sub(r"\t", " ", text)

    # Replace multiple spaces
    text = re.sub(r" +", " ", text)

    # Join wrapped lines
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    return text.strip()



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


    # 4. Chunking strategy
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )


    chunks = splitter.split_documents(docs)


    print("Total Chunks")
    print(len(chunks))



    # 5. Generate embeddings
    # 6. Save embeddings into PGVector database

    vector_store = get_vector_store(
        collection_name="regulatory_compliance"
    )


    vector_store.add_documents(chunks)


    print("Ingestion Completed")



if __name__ == "__main__":

    ingest_pdf(
        "data/Capstone_Project_1_Regulatory_Compliance_System_FAQ.pdf"
    )