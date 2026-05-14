class NarrationService:
    """
    Generuje narrację gry.
    """

    def intro(self, context: dict) -> str:
        adventure = context.get("adventure", {})
        return f"You enter {adventure.get('title', 'unknown world')}..."

    def event(self, context: dict) -> str:
        event_type = context.get("event_type")
        result = context.get("result", {})

        return f"The event ({event_type}) unfolds. Result: {result}"