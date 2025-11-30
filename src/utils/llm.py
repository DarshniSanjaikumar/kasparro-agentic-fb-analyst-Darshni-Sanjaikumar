import os
import google.generativeai as genai

class GeminiLLM:
    def __init__(self, model_name="gemini-2.5-flash", api_key=None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API key not provided or found in environment variables.")
        
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)

    def llm_call(self, prompt: str) -> str:
        """
        Send a prompt to Gemini model and return the response text.
        """
        response = self.model.generate_content(prompt)
        return response.text