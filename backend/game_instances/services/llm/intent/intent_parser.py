import re

from game.core.game_command import ALLOWED_ACTIONS as COMMAND_ACTIONS


class IntentParser:
    """Small deterministic parser for common player commands."""

    ALLOWED_ACTIONS = COMMAND_ACTIONS

    _ACTION_VARIANTS = {
        "attack": (
            "attack", "atak", "atakuję", "atakuje", "zaatakuj", "zaatakuję",
            "walczę", "walcze", "walcz", "fight", "uderzam",
        ),
        "talk": (
            "talk", "porozmawiaj", "rozmawiam", "rozmawiaj", "pytam", "zapytaj",
            "mówię", "mowie", "mów",
        ),
        "move": (
            "move", "go", "idę", "ide", "ido", "idź", "idz", "iść", "chodź", "chodz",
            "chodzić", "pójdź", "pojdz", "wejdź", "wejdz", "ruszam",
        ),
        "inspect": (
            "inspect", "look", "sprawdź", "sprawdz", "rozejrzyj", "rozglądam się",
            "rozgladam sie", "rozglądaj", "oglądam", "ogladam",
        ),
    }
    _FILLER_WORDS = {
        "a", "co", "dalej", "do", "i", "na", "o", "po", "przez", "się", "sie",
        "w", "we", "z", "za", "ze",
    }
    _TARGET_FORMS = {
        "goblina": "goblin",
        "goblinem": "goblin",
        "goblinowi": "goblin",
        "kupca": "kupiec",
        "kupcem": "kupiec",
        "kupcowi": "kupiec",
        "lasu": "las",
        "lesie": "las",
        "strażnika": "strażnik",
        "strażnikiem": "strażnik",
        "straznika": "straznik",
        "straznikiem": "straznik",
    }

    @staticmethod
    def _value(player_input):
        if isinstance(player_input, dict):
            return (
                player_input.get("message")
                or player_input.get("text")
                or player_input.get("action")
                or player_input.get("input")
                or ""
            )
        if isinstance(player_input, str):
            return player_input
        return str(player_input or "")

    @staticmethod
    def _normalise(value):
        return re.sub(r"[^\wąćęłńóśźż-]", " ", value.lower()).strip()

    @classmethod
    def _find_action(cls, text):
        for action, variants in cls._ACTION_VARIANTS.items():
            for variant in variants:
                pattern = r"(?<!\w)" + r"\s+".join(map(re.escape, variant.split())) + r"(?!\w)"
                match = re.search(pattern, text)
                if match:
                    return action, match
        return "unknown", None

    @classmethod
    def _entity_forms(cls, name):
        name = cls._normalise(str(name))
        if not name:
            return set()
        forms = {name}
        if " " not in name:
            for suffix in ("a", "ę", "em", "owi", "ie", "u", "ą"):
                forms.add(name + suffix)
            if name.endswith("iec"):
                forms.add(name[:-3] + "ca")
        return forms

    @classmethod
    def _context_target(cls, text, context, action):
        if not isinstance(context, dict):
            return None
        keys = {"attack": ("enemies",), "talk": ("npcs",), "move": ("locations",)}.get(action, ())
        candidates = []
        for key in keys:
            candidates.extend(context.get(key) or [])
        matches = []
        for candidate in candidates:
            name = candidate.get("name") if isinstance(candidate, dict) else candidate
            if not isinstance(name, str):
                continue
            for form in cls._entity_forms(name):
                if re.search(r"(?<!\w)" + re.escape(form) + r"(?!\w)", text):
                    matches.append((len(form), name))
                    break
        return max(matches, default=(0, None))[1]

    @classmethod
    def _fallback_target(cls, text, action, action_match):
        remainder = text[action_match.end():]
        words = [word for word in re.findall(r"[\wąćęłńóśźż-]+", remainder) if word]
        words = [word for word in words if word not in cls._FILLER_WORDS]
        if not words:
            return None
        target = words[0]
        return cls._TARGET_FORMS.get(target, target)

    def parse(self, player_input, context=None) -> dict:
        text = self._normalise(self._value(player_input))
        action, action_match = self._find_action(text)
        if action not in self.ALLOWED_ACTIONS:
            return {"action": "unknown", "target": None, "method": None}

        target = None
        if action != "inspect":
            target = self._context_target(text, context, action)
            if target is None and action_match is not None:
                target = self._fallback_target(text, action, action_match)

        return {"action": action, "target": target, "method": None}
