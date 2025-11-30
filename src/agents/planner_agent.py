import json
import re
from src.utils.llm import GeminiLLM


def extract_json(text):
    """Extracts JSON from AI response even when wrapped in markdown."""
    text = text.replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0).strip() if match else text


def load_prompt(file_path="prompts/planner.md"):
    """Load planner prompt template file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


class PlannerAgent:
    def __init__(self, model_name="gemini-2.5-flash"
    ""):
        self.llm = GeminiLLM(model_name=model_name)

    def run(self, user_query: str):
        """
        Call LLM with prompt, extract valid JSON,
        and ensure agent_flow is always included.
        """
        planner_prompt = load_prompt().replace("{{user_query}}", user_query)
        response = self.llm.llm_call(planner_prompt)

        try:
            clean_json = extract_json(response)
            parsed = json.loads(clean_json)

            # Ensure agent_flow exists for pipeline follow-up
            if "agent_flow" not in parsed:
                parsed["agent_flow"] = ["data_agent"]  # default fallback

            return parsed

        except json.JSONDecodeError:
            print("\n🔴 Model did not return valid JSON!")
            return {"error": "PlannerAgent: Invalid JSON response", "raw_output": response}