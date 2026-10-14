
import logging
from datetime import datetime, timezone
from io import StringIO

import pandas as pd
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from app.services.transaction_normalizer import normalize_transactions

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Upload"])

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def error_response(status_code: int, message: str):
    return JSONResponse(
        status_code=status_code,
        content={"message": message}
    )


@router.post("/csv")
async def upload_csv(file: UploadFile = File(...)):
    # 1. Validate the filename
    if not file.filename or not file.filename.lower().endswith(".csv"):
        return error_response(
            400,
            "Please upload a CSV file."
        )

    try:
        # 2. Read at most 20 MB + 1 byte
        content = await file.read(MAX_FILE_SIZE + 1)

        if len(content) > MAX_FILE_SIZE:
            return error_response(
                413,
                "The selected file exceeds the 20 MB limit."
            )

        if not content.strip():
            return error_response(
                400,
                "The uploaded CSV file is empty or invalid."
            )

        # 3. Decode the CSV
        try:
            decoded = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            return error_response(
                400,
                "The uploaded CSV file is empty or invalid."
            )

        # 4. Parse the statement and normalize transactions
        try:
            # Your current statement has 3 extra rows before its headers.
            df = pd.read_csv(
                StringIO(decoded),
                skiprows=3
            )

            if df.empty or len(df.columns) == 0:
                return error_response(
                    400,
                    "The uploaded CSV file is empty or invalid."
                )

            df.columns = df.columns.str.strip()

            transactions = normalize_transactions(df)

        except pd.errors.EmptyDataError:
            return error_response(
                400,
                "The uploaded CSV file is empty or invalid."
            )

        except (
            pd.errors.ParserError,
            ValueError,
            KeyError,
            TypeError
        ):
            return error_response(
                422,
                "Unable to parse this transaction statement."
            )

        if not transactions:
            return error_response(
                422,
                "Unable to parse this transaction statement."
            )

        # 5. Return the exact response schema expected by the frontend
        return JSONResponse(
            status_code=200,
            content={
                "fileName": file.filename,
                "importedAt": (
                    datetime.now(timezone.utc)
                    .isoformat(timespec="milliseconds")
                    .replace("+00:00", "Z")
                ),
                "transactions": transactions
            }
        )

    except Exception:
        logger.exception("Unexpected error while importing CSV")
        return error_response(
            500,
            "Unable to import the statement. Please try again."
        )

    finally:
        await file.close()
