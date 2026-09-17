import json
import logging

from game_instances.services.llm.core.llm_client import LLMClient

logger = logging.getLogger(__name__)


class NPCDialogueService:
    """Generate one NPC utterance from canonical, read-only facts."""

    def __init__(self, client=None):
        self.client = client

    @staticmethod
    def fallback(context):
        name = context.get("npc_name") or "NPC"
        return f"{name} spogląda na ciebie uważnie, ale nie odpowiada."

    def generate(self, context):
        system_prompt = (
            "STYLE INSTRUCTIONS: Speak as the NPC in Polish, in a natural dark fantasy / "
            "medieval voice, in 1–3 short sentences. No JSON, AI commentary, or backend "
            "mechanics. CANONICAL FACTS are read-only. Stay consistent with the NPC and "
            "world. Dialogue is not a game state transition. Do not claim to change HP, "
            "deal damage, grant or remove items, teleport, start or end turns, kill anyone, "
            "create a canonical quest or NPC, or change a location. Do not invent such "
            "changes as facts."
        )
        user_prompt = "CANONICAL FACTS:\n" + json.dumps(context, ensure_ascii=False)
        try:
            client = self.client or LLMClient()
            answer = client.generate(system_prompt, user_prompt)
            if isinstance(answer, str):
                answer = answer.strip()
                if answer and not answer.startswith(("{", "[", "```")):
                    return answer
        except Exception:
            logger.exception("NPC dialogue generation failed")
        return self.fallback(context)
