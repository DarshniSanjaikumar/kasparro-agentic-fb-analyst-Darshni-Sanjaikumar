# src/agents/creative_agent.py

import json

class CreativeAgent:
    def __init__(self, llm, prompt_path="prompts/creative_prompt.md"):
        self.llm = llm
        self.prompt = open(prompt_path, "r", encoding="utf-8").read()

    def run(self, low_ctr_campaigns):
        prompt_data = json.dumps(low_ctr_campaigns, indent=2)

        final_prompt = (
            self.prompt
            .replace("{{low_ctr_campaigns}}", prompt_data)
        )

        response_text = self.llm(final_prompt)

        try:
            return json.loads(response_text)
        except:
            return [{
                "campaign": "fallback",
                "new_creatives": [
                    {
                        "headline": "Special Offer!",
                        "text": "Improve your style with our best items.",
                        "cta": "Shop Now",
                        "angle": "Benefit"
                    }
                ]
            }]
