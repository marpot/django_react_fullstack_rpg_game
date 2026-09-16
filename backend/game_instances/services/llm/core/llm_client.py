import json
import re

from game_instances.services.llm.core.provider import GroqProvider, LLMProvider


INTENT_PROMPT = """You are STRICT JSON intent parser.

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


class LLMClient:
    def __init__(self, provider: LLMProvider | None = None):
        self.provider = provider if provider is not None else GroqProvider()

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return self.provider.complete(system_prompt, user_prompt)

    def generate_intent(self, system_prompt: str, user_prompt: str) -> str:
        raw = self.generate(f"{system_prompt}\n{INTENT_PROMPT}", user_prompt)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return "{}"

        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            return "{}"

        return json.dumps({
            "action": parsed.get("action"),
            "target": parsed.get("target"),
            "method": parsed.get("method"),
        })
