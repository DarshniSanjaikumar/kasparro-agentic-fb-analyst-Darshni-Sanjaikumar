import json
from src.utils.logging_utils import log_info, log_error
from src.utils.llm import GeminiLLM
import re

def extract_json(text):
    """Extracts valid JSON from AI response even if wrapped inside markdown or text."""
    text = text.replace("```json", "").replace("```", "").strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)  # Expecting list format
    if match:
        return match.group(0).strip()
    return text

class CreativeAgent:
    def __init__(self, prompt_path="prompts/creative.md"):
        self.llm = GeminiLLM()
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

    def run(self, objective, insight_output, data_agent_output=None):
        """
        Generates creative optimization strategies based on validated insights.
        """
        try:
            log_info("Running CreativeAgent to generate creative improvements...")

            # 🧠 Prepare structured final input for LLM
            structured_input = {
                "objective": objective,
                "validated_insights": insight_output,
                "campaign_performance": data_agent_output if data_agent_output else {}
            }

            # 🎯 Inject into prompt
            final_prompt = (
                self.prompt_template +
                "\n\nHere is the validated insight and context:\n" +
                json.dumps(structured_input, indent=2)
            )

            # 🚀 Call LLM
            response = self.llm.llm_call(final_prompt)

            # 🧹 Extract valid JSON
            try:
                clean_json = extract_json(response)
                return json.loads(clean_json)
            except json.JSONDecodeError:
                return {"raw_response": response, "error": "LLM did not return valid JSON"}

        except Exception as e:
            log_error(f"CreativeAgent failed: {str(e)}")
            return {"error": "CreativeAgent failed", "details": str(e)}
