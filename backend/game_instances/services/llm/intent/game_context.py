from game.core.game_command import ALLOWED_ACTIONS


class GameContextBuilder:
    MAX_TARGETS = 12
    MAX_TEXT_LENGTH = 80
    MAX_RECENT_ACTIONS = 3

    @classmethod
    def _short_text(cls, value):
        return value[:cls.MAX_TEXT_LENGTH] if isinstance(value, str) else None

    @classmethod
    def _names(cls, entities):
        names = {
            cls._short_text(getattr(entity, "name", None))
            for entity in entities
        }
        return sorted(name for name in names if name)[:cls.MAX_TARGETS]

    def build(self, state_manager, room_id, participant_id):
        room = state_manager.get_room(room_id)
        if room is None:
            return None

        player = room.players.get(participant_id)
        if player is None:
            return None

        recent_actions = [
            entry.get("action")
            for entry in room.player_histories.get(participant_id, [])[-self.MAX_RECENT_ACTIONS:]
            if isinstance(entry, dict) and entry.get("action") in ALLOWED_ACTIONS
        ]

        return {
            "current_player": self._short_text(player.name),
            "current_location": self._short_text(player.location),
            "enemies": self._names(room.enemies.values()),
            "npcs": self._names(room.npcs.values()),
            "allowed_actions": sorted(ALLOWED_ACTIONS),
            "recent_actions": recent_actions,
        }
