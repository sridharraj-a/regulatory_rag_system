from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from app.core.logger import logger
from app.services.upload_service import process_upload

router = APIRouter(
    prefix="/api/v1/upload",
    tags=["Upload"],
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document and start the ingestion pipeline.
    """

    try:

        logger.info("Received upload request.")

        if file is None:
            raise HTTPException(status_code=400, detail="No file uploaded.")

        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is missing.")

        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        # Validate file size
        contents = await file.read()

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Maximum file size is 10 MB.")

        # Reset file pointer
        await file.seek(0)

        logger.info("Processing upload: %s", file.filename)

        response = process_upload(file)

        logger.info("Upload completed successfully.")

        return response

    except HTTPException:
        raise

    except Exception as e:

        logger.exception("Upload API failed.")

        raise HTTPException(
            status_code=500, detail=f"Internal Server Error: {str(e)}"
        ) from e
