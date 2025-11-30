import pandas as pd
from datetime import timedelta
from difflib import get_close_matches
from src.utils.data_utils import load_csv_data
from src.utils.logging_utils import log_info, log_error

class DataAgent:
    def __init__(self, file_path="data/cleaned_data.csv"):
        self.file_path = file_path
        self.data = load_csv_data(file_path)

        # Normalize all column names to lowercase
        self.data.columns = self.data.columns.str.lower()

        # Create a cleaned version of campaign names for matching
        self.data["campaign_name_clean"] = (
            self.data["campaign_name"]
            .str.lower()
            .str.strip()
            .str.replace(r'\s+', ' ', regex=True)
        )

    def filter_campaign_data(self, campaign_names=None, days=None):
        """Smart filtering with support for exact, partial, and fuzzy matching."""

        df = self.data.copy()

        # 🔹 Campaign Filtering
        if campaign_names:
            # Normalize input
            if isinstance(campaign_names, list):
                campaign_names_clean = [c.lower().strip() for c in campaign_names]
            else:
                campaign_names_clean = [campaign_names.lower().strip()]

            # 🔎 Smart matching (partial / contains match)
            matched_rows = df[df["campaign_name_clean"].apply(
                lambda x: any(name in x for name in campaign_names_clean)
            )]

            # ❗ If still empty, try fuzzy matching (most similar name)
            if matched_rows.empty:
                suggestions = []
                for name in campaign_names_clean:
                    suggestions += get_close_matches(
                        name,
                        df["campaign_name_clean"].unique(),
                        n=3,
                        cutoff=0.5
                    )
                return pd.DataFrame(), list(set(suggestions))

            df = matched_rows

        # 🔹 Date Filtering
        if days and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors='ignore')
            end_date = df["date"].max()
            start_date = end_date - timedelta(days=days)
            df = df[df["date"] >= start_date]

        return df, None

    def summarize_performance(self, df):
        """Generate summary for a single campaign."""
        return {
            "total_spend": round(df["spend"].sum(), 2),
            "total_revenue": round(df["revenue"].sum(), 2),
            "avg_roas": round(df["roas"].mean(), 2),
            "avg_ctr": round(df["ctr"].mean(), 3),
            "total_clicks": int(df["clicks"].sum()),
            "total_impressions": int(df["impressions"].sum()),
            "total_purchases": int(df["purchases"].sum())
        }

    def summarize_multiple_campaigns(self, df):
        """Return separate summaries for multiple campaigns."""
        summary = {}
        for campaign in df["campaign_name_clean"].unique():
            sub_df = df[df["campaign_name_clean"] == campaign]
            summary[campaign] = self.summarize_performance(sub_df)
        return summary

    def get_peak_metric(self, df, metric):
        """Return peak metric value and associated date/campaign."""
        if metric not in df.columns or df.empty:
            return None
        peak = df.loc[df[metric].idxmax()]
        return {
            "date": str(peak["date"]) if "date" in peak else None,
            "campaign_name": peak["campaign_name"],
            metric: float(peak[metric]),
        }

    def get_daily_trends(self, df):
        """Day-wise ROAS, Spend, CTR trends for comparison."""
        df["date"] = pd.to_datetime(df["date"], errors='ignore')
        daily = df.groupby(["date", "campaign_name_clean"]).agg({
            "revenue": "sum",
            "spend": "sum",
            "roas": "mean",
            "ctr": "mean"
        }).reset_index()

        # Convert dates to string for JSON serialization
        daily["date"] = daily["date"].astype(str)
        return daily.to_dict(orient="records")

    def run(self, planner_output):
        try:
            log_info("Running DataAgent...")
            print("📈 DataAgent Initialized...")

            campaign_names = planner_output.get("campaign_name", None)
            days = planner_output.get("analysis_window_days", None)

            filtered, suggestions = self.filter_campaign_data(campaign_names, days)

            # ⚠️ No match found
            if filtered.empty:
                return {
                    "error": "No matching campaign data found.",
                    "requested_campaigns": campaign_names,
                    "suggested_campaigns": suggestions,
                    "available_campaigns": list(self.data["campaign_name"].unique())
                }

            # Detect comparison scenario
            is_comparison = isinstance(campaign_names, list) and len(campaign_names) > 1

            result = {
                "campaigns_requested": campaign_names if campaign_names else "All campaigns",
                "date_range": f"{str(filtered['date'].min().date())} to {str(filtered['date'].max().date())}",
                "campaign_summaries": (
                    self.summarize_multiple_campaigns(filtered) if is_comparison
                    else self.summarize_performance(filtered)
                ),
                "peak_spend_day": self.get_peak_metric(filtered, "spend"),
                "peak_revenue_day": self.get_peak_metric(filtered, "revenue"),
                "daily_trends": self.get_daily_trends(filtered)
            }

            return result

        except Exception as e:
            log_error(f"DataAgent failed: {str(e)}")
            return {"error": "DataAgent failed", "details": str(e)}