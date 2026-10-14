
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Analytics"])

CSV_PATH = (
    Path(__file__).resolve().parents[4]
    / "data"
    / "cleaned_transactions.csv"
)


def load_transactions():
    if not CSV_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Cleaned transaction data not found"
        )

    df = pd.read_csv(CSV_PATH)

    required = {"Date", "Transaction Type", "Amount"}
    missing = required - set(df.columns)

    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing columns: {sorted(missing)}"
        )

    # Parse dates such as 13-Oct-26
    df["Date"] = pd.to_datetime(
        df["Date"], format="%d-%b-%y", errors="coerce"
    )

    df["Amount"] = pd.to_numeric(
        df["Amount"], errors="coerce"
    )

    df["Transaction Type"] = (
        df["Transaction Type"].astype("string").str.strip().str.upper()
    )

    # Ignore invalid dates, invalid amounts, and unknown transaction types
    df = df.dropna(subset=["Date", "Amount"])
    df = df[
        df["Transaction Type"].isin(["CREDIT", "DEBIT"])
    ].copy()

    # Separate incoming and outgoing amounts
    df["Money Received"] = df["Amount"].where(
        df["Transaction Type"] == "CREDIT", 0
    )
    df["Money Spent"] = df["Amount"].where(
        df["Transaction Type"] == "DEBIT", 0
    )

    return df


def summarize(df, period):
    df = df.copy()

    # W-SUN means Monday through Sunday
    if period == "week":
        df["Period"] = (
            df["Date"].dt.to_period("W-SUN").dt.start_time
        )
        label_format = "%Y-%m-%d"
    elif period == "month":
        df["Period"] = df["Date"].dt.to_period("M").dt.start_time
        label_format = "%Y-%m"
    else:
        df["Period"] = df["Date"].dt.to_period("Y").dt.start_time
        label_format = "%Y"

    result = (
        df.groupby("Period")
        .agg(
            total_received=("Money Received", "sum"),
            total_spent=("Money Spent", "sum"),
            transaction_count=("Amount", "size"),
        )
        .reset_index()
        .sort_values("Period")
    )

    result["net_flow"] = (
        result["total_received"] - result["total_spent"]
    )

    result["period"] = result["Period"].dt.strftime(label_format)

    result = result.drop(columns=["Period"])

    # Round monetary values for presentation
    for column in ["total_received", "total_spent", "net_flow"]:
        result[column] = result[column].round(2)

    return result.to_dict(orient="records")


@router.get("/weekly")
def weekly_analytics():
    return summarize(load_transactions(), "week")


@router.get("/monthly")
def monthly_analytics():
    return summarize(load_transactions(), "month")


@router.get("/yearly")
def yearly_analytics():
    return summarize(load_transactions(), "year")
