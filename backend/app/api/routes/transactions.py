
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ...repositories.transaction_repository import load_transactions

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("")
def get_transactions(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    df = load_transactions()

    total = len(df)
    page = df.iloc[offset:offset + limit].copy()

    # Temporary IDs for the CSV-backed prototype
    page.insert(0, "id", range(offset, offset + len(page)))

    # Replace NaN/NaT values so responses are JSON-compatible
    page = page.astype(object).where(page.notna(), None)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": page.to_dict(orient="records"),
    }


@router.get("/{transaction_id}")
def get_transaction(transaction_id: int):
    df = load_transactions()

    if transaction_id < 0 or transaction_id >= len(df):
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    record = df.iloc[transaction_id].to_dict()
    record = {
        key: None if value is None or __import__("pandas").isna(value)
        else value
        for key, value in record.items()
    }

    return {"id": transaction_id, **record}

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Project root / data / cleaned_transactions.csv
CSV_PATH = (
    Path(__file__).resolve().parents[4]
    / "data"
    / "cleaned_transactions.csv"
)


@router.get("/cleaned")
def get_cleaned_transactions():
    if not CSV_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Cleaned transaction data not found"
        )

    df = pd.read_csv(CSV_PATH)

    # Make missing values JSON-compatible
    df = df.astype(object).where(pd.notna(df), None)

    return {
        "success": True,
        "count": len(df),
        "transactions": df.to_dict(orient="records")
    }