
from datetime import datetime, timezone
from uuid import uuid4

import pandas as pd


def classify_category(name: str, amount: float) -> str:
    text = name.lower()

    if any(word in text for word in [
        "salary", "income", "refund", "cashback"
    ]):
        return "Income" if amount >= 0 else "Other"

    if any(word in text for word in [
        "swiggy", "zomato", "restaurant", "food", "cafe"
    ]):
        return "Food"

    if any(word in text for word in [
        "uber", "ola", "rapido", "petrol", "fuel", "bus", "train"
    ]):
        return "Transport"

    if any(word in text for word in [
        "amazon", "flipkart", "shopping"
    ]):
        return "Shopping"

    if any(word in text for word in [
        "electricity", "recharge", "mobile bill", "internet"
    ]):
        return "Bills"

    if amount >= 0:
        return "Income"

    return "Other"


def normalize_transactions(df: pd.DataFrame) -> list[dict]:
    df = df.copy()
    df.columns = df.columns.str.strip()

    required = {
        "Date", "Time", "Transaction Details",
        "Transaction Type", "Amount"
    }
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing))}"
        )

    transactions = []
    used_ids = set()

    for _, row in df.iterrows():
        date_raw = str(row["Date"]).strip()
        time_raw = str(row["Time"]).strip()
        name = str(row["Transaction Details"]).strip()

        if not name or name.lower() == "nan":
            name = "Unknown transaction"

        # Convert amount to a numeric value
        amount_value = pd.to_numeric(row["Amount"], errors="coerce")
        if pd.isna(amount_value):
            continue

        amount = abs(float(amount_value))
        transaction_type = str(row["Transaction Type"]).strip().upper()

        if transaction_type == "DEBIT":
            amount = -amount
        elif transaction_type != "CREDIT":
            continue

        # Preserve the statement's original date/time text
        date_text = f"{date_raw} {time_raw}".strip()

        # Parse the source's date and time, assumed to be India local time
        parsed_date = pd.to_datetime(
            date_text,
            format="%d-%b-%y %I:%M %p",
            errors="coerce"
        )

        if pd.isna(parsed_date):
            iso_date = None
        else:
            india_date = parsed_date.tz_localize("Asia/Kolkata")
            iso_date = (
                india_date.astimezone(timezone.utc)
                .isoformat(timespec="milliseconds")
                .replace("+00:00", "Z")
            )

        # Use the statement ID when present; ensure uniqueness
        raw_id = row.get("Transaction ID")
        if pd.isna(raw_id) or not str(raw_id).strip():
            transaction_id = str(uuid4())
        else:
            transaction_id = str(raw_id).strip()

        if transaction_id in used_ids:
            transaction_id = f"{transaction_id}-{uuid4()}"

        used_ids.add(transaction_id)

        # The credit/debit instrument may not identify the actual method.
        # This statement is a UPI statement, so use UPI as the default.
        method = "UPI"

        transactions.append({
            "id": transaction_id,
            "name": name,
            "date": iso_date,
            "dateText": date_text,
            "amount": round(amount, 2),
            "category": classify_category(name, amount),
            "method": method
        })

    return transactions
