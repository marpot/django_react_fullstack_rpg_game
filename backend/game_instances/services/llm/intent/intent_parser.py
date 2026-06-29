class IntentParser:
    """
    Zamienia input gracza na akcję gry.
    """

    ALLOWED_ACTIONS = {
        "attack",
        "move",
        "inspect",
        "talk",
        "defend",
        "use_item",
    }

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

        action = "unknown"
        target = None
        method = None

        if has("attack", "atak", "walcz", "fight"):
            action = "attack"
        elif has("talk", "porozmawiaj", "mów"):
            action = "talk"
        elif has("move", "go", "idź", "chodź"):
            action = "move"
        elif has("inspect", "look", "sprawdź", "rozejrzyj"):
            action = "inspect"

        # bezpieczeństwo
        if action not in self.ALLOWED_ACTIONS:
            return {
                "action": "unknown",
                "target": None,
                "method": None,
            }

        words = text.split()
        if len(words) > 1:
            target = words[-1]

        return {
            "action": action,
            "target": target,
            "method": method,
        }