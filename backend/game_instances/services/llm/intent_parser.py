class IntentParser:
    """
    Zamienia input gracza na akcję gry.
    """

    def parse(self, player_input) -> dict:
        text = ""

        # --------------------------
        # NORMALIZACJA INPUTU
        # --------------------------
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

        # --------------------------
        # ATTACK
        # --------------------------
        if has("attack", "atak", "atakuj", "zaatakuj", "walcz", "fight", "hit"):
            return {
                "action": "attack",
                "target": self._target(text),
            }

        # --------------------------
        # TALK
        # --------------------------
        if has("talk", "porozmawiaj", "rozmawiaj", "gadaj", "mów"):
            return {
                "action": "talk",
                "target": self._target(text),
            }

        # --------------------------
        # MOVE
        # --------------------------
        if has("move", "go", "idź", "idz", "chodź", "wejdź", "przejdź"):
            return {
                "action": "move",
                "target": self._target(text),
            }

        # --------------------------
        # INSPECT
        # --------------------------
        if has("inspect", "look", "sprawdź", "zbadaj", "rozejrzyj", "obejrzyj"):
            return {
                "action": "inspect",
                "target": "environment",
            }

        # --------------------------
        # FALLBACK (NIE UDAWAJ INSPECT)
        # --------------------------
        return {
            "action": "unknown",
            "target": None,
            "error": "unknown_intent_fallback",
        }

    def _target(self, text: str):
        if not text:
            return None

        words = text.split()

        if len(words) < 2:
            return None

        return words[-1]