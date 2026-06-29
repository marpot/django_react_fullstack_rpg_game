import logging
from accounts.models import PlayerCharacter
from game.state.runtime.models import Player
logger = logging.getLogger(__name__)


class RuntimePlayerService:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def get_or_create(self, room_obj, user_id) -> Player:
        user_key = str(user_id)

        if not hasattr(room_obj, "players"):
            room_obj.players = {}

        player = room_obj.players.get(user_key)
        if player:
            return player  # już Player dataclass

        try:
            character = PlayerCharacter.objects.get(user_id=user_id)
        except PlayerCharacter.DoesNotExist:
            return None

        runtime_player = Player(
            id=user_id,
            name=getattr(character, "name", f"player_{user_id}"),
            hp=getattr(character, "hp", 100),
            max_hp=getattr(character, "max_health", 100),
            attack_bonus=getattr(character, "strength", 0),
            damage_die=6,
            damage_bonus=0,
            defense=getattr(character, "defense", 0),
        )

        room_obj.players[user_key] = runtime_player

        logger.info(f"[RUNTIME_PLAYER] created {runtime_player}")

        return runtime_player