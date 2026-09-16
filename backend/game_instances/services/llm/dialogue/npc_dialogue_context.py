import json


class NPCDialogueContextBuilder:
    """Select bounded, serializable facts from a resolved talk action."""

    MAX_TEXT = 160

    @classmethod
    def _text(cls, value):
        return value[:cls.MAX_TEXT] if isinstance(value, str) else None

    def build(self, talk_result, world=None, details=None):
        talk_result = talk_result if isinstance(talk_result, dict) else {}
        world = world if isinstance(world, dict) else {}
        details = details if isinstance(details, dict) else {}
        lore = world.get("lore") if isinstance(world.get("lore"), dict) else {}
        recent = details.get("recent_actions")
        if not isinstance(recent, list):
            recent = []

        context = {
            "npc_id": self._text(talk_result.get("npc_id")),
            "npc_name": self._text(talk_result.get("npc")),
            "npc_personality": self._text(talk_result.get("personality")),
            "actor": self._text(details.get("actor")),
            "location": self._text(details.get("location")),
            "player_message": self._text(details.get("player_message")),
            "world": {
                key: self._text(value)
                for key, value in (
                    ("title", world.get("title") or world.get("name")),
                    ("description", world.get("description")),
                    ("situation", lore.get("situation")),
                )
                if isinstance(value, str)
            },
            "recent_actions": [
                self._text(action) for action in recent[-3:] if isinstance(action, str)
            ],
        }
        # This also rejects any accidental non-primitive before the prompt is built.
        json.dumps(context, ensure_ascii=False)
        return context
