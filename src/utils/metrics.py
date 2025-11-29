import numpy as np
import pandas as pd

def compute_roas(revenue: float, spend: float):
    if spend == 0:
        return 0.0
    return revenue / spend

def pct_change(before: float, after: float):
    if before == 0:
        return 0.0
    return (after - before) / before

def aggregate_campaign_metrics(df):
    """Return a dictionary of summary metrics for a campaign."""
    return {
        "spend": df["spend"].sum(),
        "impressions": df["impressions"].sum(),
        "clicks": df["clicks"].sum(),
        "revenue": df["revenue"].sum(),
        "purchases": df["purchases"].sum(),
        "avg_ctr": df["ctr"].mean(),
        "avg_roas": df["roas"].mean(),
    }

def find_roas_drops(df, threshold: float):
    """
    Identify campaigns where ROAS dropped by more than 'threshold'
    between the first half and second half of the selected time window.
    """
    half = len(df) // 2
    first = df.iloc[:half]["roas"].mean()
    second = df.iloc[half:]["roas"].mean()

    drop = pct_change(first, second)

    return {
        "first_period_roas": first,
        "second_period_roas": second,
        "pct_change": drop,
        "is_drop": (drop < -threshold)
    }

def detect_low_ctr_campaigns(df, threshold: float):
    """Return rows where CTR < threshold."""
    return df[df["ctr"] < threshold]
def find_low_ctr(df, threshold: float):
    """Return rows where CTR < threshold."""
    low_ctr_df = df[df["ctr"] < threshold]
    return low_ctr_df.to_dict(orient="records")
