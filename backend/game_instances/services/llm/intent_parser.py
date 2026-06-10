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

        # --------------------------
        # ATTACK
        # --------------------------
        if any(word in text for word in ["attack", "atak", "atakuj", "zaatakuj", "hit", "fight"]):
            return {"action": "attack", "target": self._target(text)}
        
        # -------------------------
        # TALK
        # -------------------------
        if "talk" in text or "porozmawiaj" in text:
            return {"action": "talk", "target": self._target(text)}
        

         # -------------------------
        # MOVE
        # -------------------------
        if any(word in text for word in ["move", "go", "idź", "idz", "przejdź"]):
            return {"action": "move", "target": self._target(text)}

        # -------------------------
        # INSPECT
        # -------------------------
        if any(word in text for word in ["inspect", "look", "sprawdź", "zbadaj", "rozejrzyj"]):
            return {"action": "inspect", "target": "environment"}

        # -------------------------
        # FALLBACK
        # -------------------------
        return {"action": "inspect", 
                "target": "environment",
                "error": "Unkown intent - fallback inspect"
            }

    def _target(self, text: str):
        words = text.split()
        return words[-1] if len(words) > 1 else None