class NarrationContextBuilder:
    """Build a small, serializable view of an already resolved game event."""

    RESULT_FIELDS = {
        "attack": ("winner", "attacker_damage", "defender_damage"),
        "move": ("location",),
        "inspect": ("room", "enemies"),
    }
    MAX_TEXT = 120

    @classmethod
    def _text(cls, value):
        return value[:cls.MAX_TEXT] if isinstance(value, str) else None

    def build(self, action, result, world=None, details=None):
        result = result if isinstance(result, dict) else {}
        world = world if isinstance(world, dict) else {}
        details = details if isinstance(details, dict) else {}

        canonical = {}
        for key in self.RESULT_FIELDS.get(action, ()):
            value = result.get(key)
            if key in {"attacker_damage", "defender_damage"} and type(value) is int:
                canonical[key] = value
            elif key == "enemies" and isinstance(value, list):
                canonical[key] = [self._text(item) for item in value[:5] if isinstance(item, str)]
            elif isinstance(value, str):
                canonical[key] = self._text(value)

        lore = world.get("lore") if isinstance(world.get("lore"), dict) else {}
        world_excerpt = {
            key: self._text(value)
            for key, value in (
                ("title", world.get("title") or world.get("name")),
                ("description", world.get("description")),
                ("situation", lore.get("situation")),
            )
            if isinstance(value, str)
        }
        recent = details.get("recent_actions")
        if not isinstance(recent, list):
            recent = []

        return {
            "event_type": action,
            "result": canonical,
            "actor": self._text(details.get("actor")),
            "target": self._text(details.get("target")),
            "location": self._text(details.get("location")),
            "world": world_excerpt,
            "recent_actions": [
                self._text(item) for item in recent[-3:] if isinstance(item, str)
            ],
        }
