
from pathlib import Path

import pandas as pd
from fastapi import HTTPException

# Project root: pocket_money_transaction/
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CSV_PATH = PROJECT_ROOT / "data" / "raw.csv"


def load_transactions() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="Transaction CSV file was not found."
        )

    try:
        df = pd.read_csv(CSV_PATH)
    except (OSError, UnicodeError, pd.errors.ParserError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to read the transaction CSV."
        ) from exc

    # Normalize headers, e.g. "Transaction Date" -> "transaction_date"
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )

    return df
