from game_instances.services.llm.core.llm_client import LLMClient

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
        world = context.get("world") or {}
        event_type = context.get("event_type")
        result = context.get("result") or {}

        system_prompt = """
You are a DARK FANTASY RPG narrator.
Respond in Polish.
2–4 sentences.
No JSON.
No explanations.
"""

        user_prompt = f"""
EVENT TYPE: {event_type}

RESULT:
{result}

WORLD:
{world}
"""

        llm_output = self.client.generate(system_prompt, user_prompt)

        if llm_output:
            return llm_output

        return f"Zdarzenie ({event_type}) się rozwija."