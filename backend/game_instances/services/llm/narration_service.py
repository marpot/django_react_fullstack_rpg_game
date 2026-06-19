from .llm_client import LLMClient

class NarrationService:
    """
    Generuje narrację gry.
    """
    def __init__(self):
        self.client = LLMClient()

    def intro(self, context: dict) -> str:
        world = context.get("world")
        adventure = context.get("adventure", {})

        if world and world.get("intro"):
            return world["intro"]

        return f"You enter {adventure.get('title', 'unknown world')}..."

    def event(self, context: dict) -> str:
        world = context.get("world")
        event_type = context.get("event_type")
        result = context.get("result", {})

        # prompt budowany zawsze
        prompt = {
            "event_type": event_type,
            "result": result,
            "world": world or {}
        }

        llm_output = self.client.generate(str(prompt))

        # fallback (jeśli LLM coś zwróci)
        if llm_output:
            return llm_output

        if world and world.get("situation"):
            return world["situation"]

        return f"The event ({event_type}) unfolds. Result: {result}"