# src/agents/data_agent.py

import json
from src.utils.data_utils import DataUtils
from src.utils.metrics import find_roas_drops, find_low_ctr


class DataAgent:
    
    def __init__(self, config, llm, prompt_path="prompts/data_summary_prompt.md"):
        self.config = config
        self.llm = llm
        self.prompt = open(prompt_path, "r", encoding="utf-8").read()

        # Initialize DataUtils containing the dataset path
        self.utils = DataUtils(self.config["data"]["path"])

    def run(self):

        # Load and summarize data using your class
        df = self.utils.load_data()
        overall = self.utils.summarize_overall(df)
        campaign_summary = self.utils.summarize_by_campaign(df)

        # Detect ROAS drops and low CTR campaigns
        roas_drops = find_roas_drops(
            campaign_summary,
            threshold=self.config["thresholds"]["roas_drop_pct"]
        )

        low_ctr = find_low_ctr(
            campaign_summary,
            threshold=self.config["thresholds"]["low_ctr"]
        )

        # Build summary for the LLM
        summary = {
            "overall_trends": overall,
            "campaign_summary": campaign_summary.to_dict(orient="records"),
            "top_roas_drops": roas_drops,
            "low_ctr_campaigns": low_ctr
        }

        # Build prompt
        llm_prompt = self.prompt.replace("{{data_summary}}", json.dumps(summary, indent=2))

        # LLM call
        response_text = self.llm(llm_prompt)

        # Return LLM JSON output or fallback summary
        try:
            return json.loads(response_text)
        except:
            return summary
