class NarrationService:
    """
    Generuje narrację gry.
    """

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

        if world and world.get("situation"):
            return world["situation"]

        return f"The event ({event_type}) unfolds. Result: {result}"