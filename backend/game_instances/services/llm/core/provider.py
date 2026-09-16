import os
from typing import Protocol

from openai import OpenAI


class LLMProvider(Protocol):
    def complete(self, system_prompt: str, user_prompt: str) -> str: ...


class GroqProvider:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
        self._client = None

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if self._client is None:
            self._client = OpenAI(
                api_key=os.getenv("GROQ_API_KEY"),
                base_url=os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1"),
            )
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=200,
        )
        return response.choices[0].message.content or ""
