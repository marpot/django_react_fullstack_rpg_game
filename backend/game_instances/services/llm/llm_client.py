from openai import OpenAI
import os

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY")
            base_url=os.getenv("GROQ_API_BASE_URL")
        )

    def generate(self, prompt:str) -> str:
        return f"[MOCK LLM RESPONSE]: {prompt}"
    