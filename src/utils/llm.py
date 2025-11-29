# src/utils/llm.py

import os
from groq import Groq

class LLM:
    def __init__(self, model="llama-3.1-8b-instant"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set in environment variables!")

        self.client = Groq(api_key=api_key)
        self.model = model

    def __call__(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        # FIX: Groq returns message object, not dictionary
        return response.choices[0].message.content
