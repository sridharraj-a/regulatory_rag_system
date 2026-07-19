from fastapi import APIRouter, UploadFile, File

from app.services.upload_service import process_upload

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/")
async def upload_document(file: UploadFile = File(...)):

    response = process_upload(file)

    return response
