import logging

logger = logging.getLogger(__name__)


class InspectAction:
    def __init__(self, state_manager, runtime_player_service, choice_service, narrate_fn, response_fn):
        self.state_manager = state_manager
        self.runtime_player_service = runtime_player_service
        self.choice_service = choice_service
        self.narrate_fn = narrate_fn
        self.response_fn = response_fn

    def handle(self, parsed_input, world=None):
        room = parsed_input.get("room")
        participant_id = parsed_input.get("participant_id")

        room_key = self.state_manager.normalize_room_id(room)
        room_obj = self.state_manager.get_or_create_room(room_key)

        self.runtime_player_service.get_or_create(room_obj, participant_id)

        enemies = list(room_obj.enemies.keys())

        narration = self.narrate_fn(
            "inspect",
            {
                "room": room_key,
                "enemies": enemies
            },
            world,
        )

        choices = self.choice_service.build_choices(
            adventure_id=parsed_input.get("adventure"),
            room_key=room_key,
            event_type="inspect",
            result={"room": room_key, "enemies": enemies},
            world=world,
        )

        return self.response_fn(
            "inspect",
            narration.get("text", "Rozglądasz się po okolicy"),
            {"room": room_key, "enemies": enemies},
            world,
            choices,
        )