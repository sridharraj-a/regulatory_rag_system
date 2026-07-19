import os
import shutil

from ingestion.ingestion import ingest_pdf


UPLOAD_FOLDER = "data"


def save_uploaded_file(file):

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    print("Saving file:", file_path)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    print("File saved successfully")

    return file_path



def process_upload(file):

    print("Upload started")


    # 1. Save file
    file_path = save_uploaded_file(file)


    print("Starting ingestion")


    # 2. Run ingestion pipeline
    ingest_pdf(file_path)


    print("Ingestion completed")


    return {
        "message": "File uploaded and indexed successfully",
        "file": file.filename
    }