import os
import shutil

from fastapi import HTTPException, UploadFile

from app.core.logger import logger
from app.ingestion.ingestion import ingest_pdf

UPLOAD_FOLDER = os.path.join("app", "data")

ALLOWED_EXTENSIONS = {".pdf"}


def save_uploaded_file(file: UploadFile) -> str:
    """
    Save uploaded PDF into the data folder.
    """

    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        file_path = os.path.join(
            UPLOAD_FOLDER,
            file.filename,
        )

        # Optional: Prevent duplicate uploads
        if os.path.exists(file_path):
            raise HTTPException(
                status_code=409,
                detail="File already exists."
            )

        logger.info("Saving file: %s", file_path)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info("File saved successfully.")

        return file_path

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Error while saving uploaded file.")

        raise RuntimeError(
            f"Unable to save uploaded file: {str(e)}"
        ) from e


def process_upload(file: UploadFile):
    """
    Save uploaded PDF and start ingestion.
    """

    try:

        logger.info("========== FILE UPLOAD STARTED ==========")

        if file is None:
            raise HTTPException(
                status_code=400,
                detail="No file uploaded."
            )

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is missing."
            )

        extension = os.path.splitext(file.filename)[1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported."
            )

        logger.info("Uploading file: %s", file.filename)

        file_path = save_uploaded_file(file)

        logger.info("Starting ingestion...")

        ingest_pdf(file_path)

        logger.info("Ingestion completed successfully.")

        return {
            "status": "success",
            "message": "File uploaded and indexed successfully.",
            "file_name": file.filename,
            "location": file_path,
        }

    except HTTPException:
        raise

    except Exception as e:

        logger.exception("Upload failed.")

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        ) from e