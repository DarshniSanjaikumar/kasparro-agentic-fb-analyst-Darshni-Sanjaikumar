import json
import re
from src.utils.logging_utils import log_info, log_error
from src.utils.llm import GeminiLLM


def extract_json(text):
    """Extracts valid JSON even if wrapped in markdown or explanation."""
    text = text.replace("```json", "").replace("```", "").strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)  # Insight returns a list
    if match:
        return match.group(0).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)  # Backup for dict format
    return match.group(0).strip() if match else text


class InsightAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.llm = GeminiLLM(model_name=model_name)

    def run(self, data_agent_output, objective):
        """
        Receives structured DataAgent output and planner objective,
        generates hypothesis-driven insights using LLM.
        """

        try:
            log_info("Running InsightAgent to generate hypotheses...")

            # Load structured prompt template
            with open("prompts/insight.md", "r", encoding="utf-8") as file:
                prompt_template = file.read()

            # Build final LLM prompt
            final_prompt = (
                prompt_template
                + "\n\n📌 Planner Objective:\n"
                + json.dumps(objective, indent=2)
                + "\n\n📊 Data Summary Received:\n"
                + json.dumps(data_agent_output, indent=2)
            )

            # Call the model
            llm_response = self.llm.llm_call(final_prompt)

            # Extract JSON hypothesis from LLM output
            try:
                clean_json = extract_json(llm_response)
                return json.loads(clean_json)
            except json.JSONDecodeError:
                log_error("InsightAgent: Model returned invalid JSON.")
                return {"error": "InsightAgent: Invalid JSON format", "raw_output": llm_response}

        except Exception as e:
            log_error(f"InsightAgent failed: {str(e)}")
            return {"error": "InsightAgent runtime failure", "details": str(e)}
