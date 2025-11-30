import pandas as pd
from typing import Optional
from src.utils.logging_utils import log_info, log_error


def load_csv_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    Loads a CSV file into a cleaned pandas DataFrame.
    
    Enhancements:
    - Validates file existence and readability
    - Normalizes column names (lowercase, trim spaces)
    - Converts 'date' column to datetime format (if present)
    - Adds robust logging for success and failure
    - Returns None instead of empty DataFrame on critical failure
    """
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)

        # Standardize column names
        df.columns = df.columns.str.lower().str.strip()

        # Convert date column (if present)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        log_info(
            f"📄 Successfully loaded dataset: {file_path} | "
            f"Rows: {len(df)} | Columns: {list(df.columns)}"
        )
        return df

    except FileNotFoundError:
        log_error(f"❌ File not found: {file_path}")
        return None

    except pd.errors.EmptyDataError:
        log_error(f"⚠ Empty CSV file: {file_path}")
        return None

    except Exception as e:
        log_error(f"🚨 Error loading CSV ({file_path}): {str(e)}")
        return None
