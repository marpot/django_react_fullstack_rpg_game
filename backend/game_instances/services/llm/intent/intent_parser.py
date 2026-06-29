class IntentParser:
    """
    Zamienia input gracza na akcję gry.
    """

    def parse(self, player_input) -> dict:
        text = ""

        if isinstance(player_input, dict):
            text = (
                player_input.get("message")
                or player_input.get("text")
                or player_input.get("action")
                or player_input.get("input")
                or ""
            )
        elif isinstance(player_input, str):
            text = player_input
        else:
            text = str(player_input or "")

        text = text.lower().strip()

        def has(*keywords: str) -> bool:
            return any(k in text for k in keywords)

        if has("attack", "atak", "walcz", "fight"):
            return {"action": "attack", "target": self._target(text)}

        if has("talk", "porozmawiaj", "mów"):
            return {"action": "talk", "target": self._target(text)}

        if has("move", "go", "idź", "chodź"):
            return {"action": "move", "target": self._target(text)}

        if has("inspect", "look", "sprawdź", "rozejrzyj"):
            return {"action": "inspect", "target": "environment"}

        return {
            "action": "unknown",
            "target": None,
            "error": "unknown_intent_fallback",
        }

    def _target(self, text: str):
        words = text.split()
        return words[-1] if len(words) > 1 else None