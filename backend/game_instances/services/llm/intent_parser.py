class IntentParser:
    """
    Zamienia input gracza na akcję gry.
    """

    ALLOWED_ACTIONS = [
        "move",
        "inspect",
        "talk",
        "attack",
        "defend",
        "use_item",
    ]

    def parse(self, player_input: str) -> dict:
        text = player_input.lower()

        if "attack" in text:
            return {"action": "attack", "target": self._target(text)}

        if "talk" in text:
            return {"action": "talk", "target": self._target(text)}

        if "move" in text or "go" in text:
            return {"action": "move", "target": self._target(text)}

        if "inspect" in text or "look" in text:
            return {"action": "inspect", "target": "environment"}

        return {"action": "inspect", "target": None}

    def _target(self, text: str):
        words = text.split()
        return words[-1] if len(words) > 1 else None