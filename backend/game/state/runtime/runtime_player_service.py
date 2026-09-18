import logging

from chat.models import RoomParticipant
from game.state.runtime.models import Player

logger = logging.getLogger(__name__)


class RuntimePlayerService:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def get_or_create(self, room_obj, participant_id: int, participant=None) -> Player | None:
        if participant_id is None:
            return None

        if not hasattr(room_obj, "players"):
            room_obj.players = {}

        player = room_obj.players.get(participant_id)
        if player is not None:
            return player

        if participant is None:
            try:
                participant = (
                    RoomParticipant.objects
                    .select_related("user", "character")
                    .get(id=participant_id, room_id=room_obj.name)
                )
            except RoomParticipant.DoesNotExist:
                logger.warning(
                    "[RUNTIME_PLAYER] participant not found: %s",
                    participant_id,
                )
                return None

        if participant.is_ai:
            runtime_player = Player(
                id=participant.id,
                user_id=None,
                character_id=None,
                name=participant.name,
                hp=100,
                max_hp=100,
                attack_bonus=0,
                damage_die=6,
                damage_bonus=0,
                defense=0,
            )
        else:
            character = participant.character

            if character is None or character.user_id != participant.user_id:
                logger.warning(
                    "[RUNTIME_PLAYER] human participant %s has no valid owned character",
                    participant.id,
                )
                return None

            runtime_player = Player(
                id=participant.id,
                user_id=participant.user_id,
                character_id=character.id,
                name=character.name,
                hp=character.health,
                max_hp=character.max_health,
                attack_bonus=character.strength,
                damage_die=6,
                damage_bonus=0,
                defense=0,
            )

        room_obj.players[participant.id] = runtime_player

        logger.info("[RUNTIME_PLAYER] created %s", runtime_player)

        return runtime_player
