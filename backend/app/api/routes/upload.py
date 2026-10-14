
from datetime import datetime, timezone
from io import BytesIO, StringIO

import pandas as pd
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from app.services.transaction_normalizer import normalize_transactions

router = APIRouter(tags=["Upload"])

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/csv")
async def upload_csv(file: UploadFile = File(...)):
    # Validate filename and extension
    if not file.filename or not file.filename.lower().endswith(".csv"):
        return JSONResponse(
            status_code=400,
            content={"message": "Please upload a CSV file."}
        )

    try:
        # Read at most 20 MB + 1 byte to detect oversized files
        content = await file.read(MAX_FILE_SIZE + 1)

        if len(content) > MAX_FILE_SIZE:
            return JSONResponse(
                status_code=413,
                content={
                    "message": "The selected file exceeds the 20 MB limit."
                }
            )

        if not content.strip():
            return JSONResponse(
                status_code=400,
                content={
                    "message": "The uploaded CSV file is empty or invalid."
                }
            )

        # Decode CSV content
        try:
            decoded = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "The uploaded CSV file is empty or invalid."
                }
            )

        # This matches your statement format: actual headers are on row 4.
        try:
            df = pd.read_csv(StringIO(decoded), skiprows=3)

            if df.empty or len(df.columns) == 0:
                return JSONResponse(
                    status_code=400,
                    content={
                        "message": "The uploaded CSV file is empty or invalid."
                    }
                )

            df.columns = df.columns.str.strip()
            transactions = normalize_transactions(df)

        except pd.errors.EmptyDataError:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "The uploaded CSV file is empty or invalid."
                }
            )
        except (pd.errors.ParserError, ValueError, KeyError):
            return JSONResponse(
                status_code=422,
                content={
                    "message": "Unable to parse this transaction statement."
                }
            )

        if not transactions:
            return JSONResponse(
                status_code=422,
                content={
                    "message": "Unable to parse this transaction statement."
                }
            )

        return JSONResponse(
            status_code=200,
            content={
                "fileName": file.filename,
                "importedAt": datetime.now(timezone.utc).isoformat(
                    timespec="milliseconds"
                ).replace("+00:00", "Z"),
                "transactions": transactions
            }
        )

    except Exception:
        # Log the real exception server-side in production.
        return JSONResponse(
            status_code=500,
            content={
                "message": "Unable to import the statement. Please try again."
            }
        )

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
