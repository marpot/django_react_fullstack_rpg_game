import logging

logger = logging.getLogger(__name__)


class MoveAction:
    def __init__(
        self,
        state_manager,
        runtime_player_service,
        choice_service,
        narrate_fn,
        response_fn,
        resolver=None,
    ):
        self.state_manager = state_manager
        self.runtime_player_service = runtime_player_service
        self.choice_service = choice_service
        self.narrate_fn = narrate_fn
        self.response_fn = response_fn
        self.resolver = resolver

    def handle(self, parsed_input, world=None):
        room = parsed_input.get("room")
        participant_id = parsed_input.get("participant_id")
        target = parsed_input.get("target")

        room_key = self.state_manager.normalize_room_id(room)
        room_obj = self.state_manager.get_or_create_room(room_key)

        player = self.runtime_player_service.get_or_create(room_obj, participant_id)

        if not player:
            return self.response_fn(
                "move",
                "Player not found",
                {"error": "no_player"},
            )

        player.location = target or "unknown"

        narration = self.narrate_fn(
            "move",
            {"location": player.location},
            world,
        )

        choices = self.choice_service.build_choices(
            enemies=room_obj.enemies,
            npcs=room_obj.npcs,
        )

        return self.response_fn(
            "move",
            narration.get("text", f"Przemieszczasz się do: {player.location}"),
            {"location": player.location},
            world,
            choices,
        )
