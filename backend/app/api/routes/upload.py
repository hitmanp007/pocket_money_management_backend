
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/upload", tags=["File Upload"])


@router.post("/csv")
async def upload_csv(file: UploadFile = File(...)):
    # Validate file extension
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file."
        )

    # Read the uploaded file to verify that it was received.
    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded CSV file is empty."
        )

    return {
        "success": True,
        "message": "Received the file",
        "filename": file.filename,
        "size_bytes": len(content)
    }
