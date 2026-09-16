from game.core.game_command import ALLOWED_ACTIONS as COMMAND_ACTIONS


class IntentParser:
    """
    Zamienia input gracza na akcję gry.
    """

    ALLOWED_ACTIONS = COMMAND_ACTIONS

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
        elif has("talk", "porozmawiaj", "mów", "rozmawiaj"):
            action = "talk"
        elif has("move", "go", "idź", "idz", "iść", "ido", "idę", "chodź", "chodzić", "pójdź", "wejdź"):
            action = "move"
        elif has("inspect", "look", "sprawdź", "sprawdz", "rozejrzyj", "rozglądaj"):
            action = "inspect"

        if action not in self.ALLOWED_ACTIONS:
            return {
                "action": "unknown",
                "target": None,
                "method": None,
            }

        if action == "move":
            words = [w for w in text.replace("-", " ").split() if w]
            if len(words) > 1:
                target_tokens = [w for w in words[1:] if w not in {"do", "na", "do", "przez", "w", "na", "ku"}]
                target = " ".join(target_tokens).strip()
                if not target:
                    target = words[-1]
        else:
            words = text.split()
            if len(words) > 1:
                target = words[-1]

        return {
            "action": action,
            "target": target,
            "method": method,
        }
