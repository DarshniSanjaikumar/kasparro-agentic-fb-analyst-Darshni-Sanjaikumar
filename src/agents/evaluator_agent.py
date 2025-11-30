import json
import re
from src.utils.logging_utils import log_info, log_error
from src.utils.llm import GeminiLLM


def extract_json(text):
    """Extracts valid JSON from AI response even if wrapped inside markdown or text."""
    text = text.replace("```json", "").replace("```", "").strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)  # Expecting list format
    if match:
        return match.group(0).strip()
    return text


class EvaluatorAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.llm = GeminiLLM(model_name=model_name)

    def run(self, objective, data_agent_output, insight_output):
        """
        Receives planner objective, structured DataAgent output, 
        and InsightAgent hypotheses to validate whether
        the insights are supported by actual evidence.
        """

        try:
            log_info("Running EvaluatorAgent to validate insights...")

            # Load evaluator prompt template
            with open("prompts/evaluator.md", "r", encoding="utf-8") as f:
                prompt_template = f.read()

            # Construct LLM prompt
            final_prompt = (
                prompt_template
                + "\n\n📌 Planner Objective:\n"
                + json.dumps(objective, indent=2)
                + "\n\n📊 Structured Data Summary:\n"
                + json.dumps(data_agent_output, indent=2)
                + "\n\n💡 Hypotheses to Evaluate:\n"
                + json.dumps(insight_output, indent=2)
            )

            # Call to LLM
            llm_response = self.llm.llm_call(final_prompt)

            # Extract JSON from AI output
            try:
                clean_json = extract_json(llm_response)
                return json.loads(clean_json)
            except json.JSONDecodeError:
                log_error("EvaluatorAgent: Invalid JSON returned.")
                return {"error": "EvaluatorAgent: Invalid LLM output", "raw_output": llm_response}

        except Exception as e:
            log_error(f"EvaluatorAgent failed: {str(e)}")
            return {"error": "EvaluatorAgent runtime failure", "details": str(e)}