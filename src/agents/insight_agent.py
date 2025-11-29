# src/agents/insight_agent.py

import json

class InsightAgent:
    def __init__(self, llm, prompt_path="prompts/insight_prompt.md"):
        self.llm = llm
        self.prompt = open(prompt_path, "r", encoding="utf-8").read()

    def run(self, data_summary, user_query):
        final_prompt = (
            self.prompt
            .replace("{{user_query}}", user_query)
            .replace("{{data_summary}}", json.dumps(data_summary, indent=2))
        )

        response_text = self.llm(final_prompt)

        try:
            return json.loads(response_text)
        except:
            return [{
                "hypothesis_id": "fallback",
                "hypothesis": "ROAS likely dropped due to CTR decline.",
                "metrics_considered": ["ctr", "roas"]
            }]
