from openai import OpenAI
import os
import re
import json


class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url=os.getenv("GROQ_API_BASE_URL", "https://api.groq.com/openai/v1"),
        )
        self.model = "llama-3.3-70b-versatile"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        system_prompt
                        + "\n"
                        + """
You are STRICT JSON intent parser.

Return ONLY this schema:

{
  "action": "attack|move|inspect|talk|defend|use_item",
  "target": string or null,
  "method": string or null
}

RULES:
- NO extra fields
- NO hp
- NO damage
- NO result
- NO message
- ONLY JSON
"""
                    )
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=200,
        )

        raw = response.choices[0].message.content or ""

        # wyciągnij JSON
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return "{}"

        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            return "{}"

        # 🔥 HARD FILTER (to jest klucz)
        return json.dumps({
            "action": parsed.get("action"),
            "target": parsed.get("target"),
            "method": parsed.get("method"),
        })