# src/agents/planner_agent.py

import json

class PlannerAgent:
    def __init__(self, llm, prompt_path="prompts/planner_prompt.md"):
        self.llm = llm
        self.prompt = open(prompt_path, "r", encoding="utf-8").read()

    def run(self, user_query: str):
        prompt = self.prompt.replace("{{user_query}}", user_query)

        response_text = self.llm(prompt)

        try:
            return json.loads(response_text)
        except:
            return {
                "tasks": [
                    "load_data",
                    "generate_summary",
                    "generate_insights",
                    "validate_insights",
                    "generate_creatives",
                ],
                "needs_creatives": True,
                "analysis_window_days": 30
            }
