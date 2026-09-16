import logging
import json
import re

from game.core.narration_fallback import narration_fallback
from game_instances.services.llm.core.llm_client import LLMClient


logger = logging.getLogger(__name__)


class NarrationService:
    """
    Generuje narrację RPG (story layer).
    """

    def __init__(self):
        self.client = LLMClient()

    def intro(self, context: dict) -> str:
        world = context.get("world") or {}
        adventure = context.get("adventure") or {}

        if world.get("intro"):
            return world["intro"]

        return f"You enter {adventure.get('title', 'unknown world')}..."

    def event(self, context: dict) -> str:
        event_type = context.get("event_type")
        result = context.get("result") or {}

        system_prompt = (
            "STYLE INSTRUCTIONS: Write a short dark fantasy / medieval narration in Polish, "
            "2–4 sentences. No JSON or meta commentary about mechanics or AI. "
            "CANONICAL FACTS are authoritative. Describe only the action and its confirmed "
            "result. Never change numbers or action outcome, invent mechanical effects, "
            "declare death unless dead=true is explicitly present, or introduce new items, "
            "characters or locations as facts. If a fact is absent, leave it unstated."
        )
        user_prompt = "CANONICAL FACTS:\n" + json.dumps(context, ensure_ascii=False)

        try:
            llm_output = self.client.generate(system_prompt, user_prompt)
        except Exception:
            logger.exception("LLM event narration failed")
            llm_output = None

        if isinstance(llm_output, str) and llm_output.strip():
            text = llm_output.strip()
            if text.startswith(("{", "[", "```")):
                return narration_fallback(event_type, result)
            numbers = set(re.findall(r"\d+", text))
            canonical_numbers = {
                str(value) for value in result.values() if type(value) is int
            }
            claims_death = re.search(
                r"\b(?:ginie|zgin\w*|umier\w*|martw\w*|zabij\w*|śmier\w*)\b",
                text, re.IGNORECASE,
            )
            if numbers <= canonical_numbers and (not claims_death or result.get("dead") is True):
                return text

        return narration_fallback(event_type, result)
