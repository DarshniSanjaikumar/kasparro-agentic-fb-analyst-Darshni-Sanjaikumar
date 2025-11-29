# src/agents/evaluator_agent.py

import json
from src.utils.metrics import pct_change

class EvaluatorAgent:
    def __init__(self, df, llm=None, prompt_path="prompts/evaluator_prompt.md"):
        self.df = df
        self.llm = llm
        self.prompt = open(prompt_path, "r", encoding="utf-8").read()

    def validate_one(self, h):
        campaign = h.get("campaign")
        if not campaign:
            return {
                "hypothesis_id": h.get("hypothesis_id", "unknown"),
                "validated": False,
                "confidence": 0.1,
                "notes": "Missing campaign name"
            }

        subset = self.df[self.df["campaign_name"] == campaign]
        if len(subset) < 3:
            return {
                "hypothesis_id": h.get("hypothesis_id"),
                "validated": False,
                "confidence": 0.15,
                "notes": "Not enough rows to validate"
            }

        half = len(subset) // 2
        before = subset.iloc[:half]
        after = subset.iloc[half:]

        evidence = {
            "ctr_change_pct": pct_change(before["ctr"].mean(), after["ctr"].mean()),
            "roas_change_pct": pct_change(before["roas"].mean(), after["roas"].mean()),
            "spend_change_pct": pct_change(before["spend"].mean(), after["spend"].mean()),
        }

        validated = evidence["roas_change_pct"] < 0
        confidence = min(1, max(0.1, abs(evidence["roas_change_pct"]) / 0.5))

        return {
            "hypothesis_id": h["hypothesis_id"],
            "validated": validated,
            "confidence": round(confidence, 2),
            "evidence": evidence,
            "notes": "Supported by data" if validated else "Weak support"
        }

    def run(self, hypotheses):
        return [self.validate_one(h) for h in hypotheses]
