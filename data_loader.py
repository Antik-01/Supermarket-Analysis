"""
data_loader.py
Handles loading, validating, and cleaning the supermarket sales CSV dataset.
"""

import pandas as pd
import numpy as np
from pathlib import Path


EXPECTED_COLUMNS = [
    "Invoice ID", "Branch", "City", "Customer type", "Gender",
    "Product line", "Unit price", "Quantity", "Tax 5%", "Sales",
    "Date", "Time", "Payment", "cogs", "gross margin percentage",
    "gross income", "Rating",
]

NUMERIC_COLUMNS = ["Unit price", "Quantity", "Tax 5%", "Sales", "cogs",
                   "gross margin percentage", "gross income", "Rating"]


def load_data(csv_path: str) -> pd.DataFrame:
    """Load the CSV file and return a raw DataFrame."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at: {csv_path}")
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    return df


def validate_columns(df: pd.DataFrame) -> dict:
    """
    Check which expected columns are present/missing.
    Returns a dict with keys 'present' and 'missing'.
    """
    present = [c for c in EXPECTED_COLUMNS if c in df.columns]
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    return {"present": present, "missing": missing}


def audit_data_quality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a summary DataFrame showing per-column quality metrics:
    dtype, missing count, missing %, duplicate rows, zero-value count.
    """
    total = len(df)
    rows = []
    for col in df.columns:
        missing_n = df[col].isna().sum()
        missing_pct = round(missing_n / total * 100, 2)
        zeros = int((df[col] == 0).sum()) if df[col].dtype in [np.float64, np.int64] else "-"
        rows.append({
            "Column": col,
            "Data Type": str(df[col].dtype),
            "Missing Count": missing_n,
            "Missing %": missing_pct,
            "Zero Count": zeros,
        })
    summary = pd.DataFrame(rows)
    return summary


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Clean the dataset:
    - Drop fully duplicate rows
    - Coerce numeric columns to numeric (invalid → NaN)
    - Fill missing numeric values with column median
    - Parse Date column to datetime
    - Recalculate Sales = Quantity × Unit Price (step 3 requirement)
    - Add derived columns: Month, Day of Week, Hour

    Returns (cleaned_df, cleaning_log).
    """
    log = {}
    original_rows = len(df)

    # Drop exact duplicates
    df = df.drop_duplicates()
    log["duplicate_rows_dropped"] = original_rows - len(df)

    # Coerce numeric columns
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            before_nulls = df[col].isna().sum()
            df[col] = pd.to_numeric(df[col], errors="coerce")
            after_nulls = df[col].isna().sum()
            new_nulls = int(after_nulls - before_nulls)
            if new_nulls > 0:
                log[f"{col}_coercion_nulls"] = new_nulls

    # Fill missing numerics with median
    filled = {}
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            n = df[col].isna().sum()
            if n > 0:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                filled[col] = {"filled": int(n), "with_median": round(median_val, 4)}
    if filled:
        log["median_filled"] = filled

    # Recalculate Sales = Quantity × Unit Price (requirement step 3)
    if "Quantity" in df.columns and "Unit price" in df.columns:
        df["Calculated Sales"] = df["Quantity"] * df["Unit price"]
        log["sales_recalculated"] = True

    # Parse Date
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Month"] = df["Date"].dt.month_name()
        df["Month_num"] = df["Date"].dt.month
        df["Day of Week"] = df["Date"].dt.day_name()
        df["Hour"] = pd.to_datetime(df["Time"], format="%I:%M:%S %p", errors="coerce").dt.hour

    log["final_rows"] = len(df)
    log["final_columns"] = len(df.columns)
    return df, log
