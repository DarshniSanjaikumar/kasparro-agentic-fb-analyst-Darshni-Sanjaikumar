import pandas as pd
from datetime import datetime, timedelta

class DataUtils:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path

    def load_data(self):
        df = pd.read_csv(self.csv_path)

        # Fix datetime
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])

        # Fill basic nulls
        df = df.fillna({
            "spend": 0,
            "impressions": 0,
            "clicks": 0,
            "purchases": 0,
            "revenue": 0,
            "roas": 0,
            "ctr": 0
        })

        return df

    def filter_by_date(self, df, days: int):
        """Select only the last X days of data."""
        max_date = df["date"].max()
        start_date = max_date - timedelta(days=days)
        return df[(df["date"] >= start_date) & (df["date"] <= max_date)]

    def group_by_date(self, df):
        """Daily-level metrics."""
        return (
            df.groupby("date")
            .agg({
                "spend": "sum",
                "impressions": "sum",
                "clicks": "sum",
                "purchases": "sum",
                "revenue": "sum",
                "ctr": "mean",
                "roas": "mean",
            })
            .reset_index()
        )

    def group_by_campaign(self, df):
        """Campaign-level aggregated metrics."""
        return (
            df.groupby("campaign_name")
            .agg({
                "spend": "sum",
                "impressions": "sum",
                "clicks": "sum",
                "purchases": "sum",
                "revenue": "sum",
                "ctr": "mean",
                "roas": "mean",
            })
            .reset_index()
        )

    def group_by_audience(self, df):
        return (
            df.groupby("audience_type")
            .agg({
                "spend": "sum",
                "impressions": "sum",
                "clicks": "sum",
                "purchases": "sum",
                "revenue": "sum",
                "ctr": "mean",
                "roas": "mean",
            })
            .reset_index()
        )
    def summarize_overall(self, df):
        total_spend = df["spend"].sum()
        total_revenue = df["revenue"].sum()
        total_clicks = df["clicks"].sum()
        total_impressions = df["impressions"].sum()
        total_purchases = df["purchases"].sum()

        overall_summary = {
            "total_spend": total_spend,
            "total_revenue": total_revenue,
            "total_clicks": total_clicks,
            "total_impressions": total_impressions,
            "total_purchases": total_purchases,
            "overall_roas": total_revenue / total_spend if total_spend > 0 else 0,
            "overall_ctr": total_clicks / total_impressions if total_impressions > 0 else 0,
        }

        return overall_summary
    def summarize_by_campaign(self, df):
        campaign_summary = self.group_by_campaign(df)
        return campaign_summary
