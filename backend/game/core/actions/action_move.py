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

        exits = self.state_manager.get_exits(room_obj, player)
        destination = None
        for choice in exits:
            candidate = choice.next_location
            if isinstance(target, str) and target.strip().casefold() in {
                str(candidate.id), candidate.title.casefold()
            }:
                destination = candidate
                break

        if destination is None:
            return self.response_fn(
                "move", "Nie ma takiego przejścia", {"error": "invalid_exit"},
            )

        destination_id = str(destination.id)
        for room_player in room_obj.players.values():
            room_player.location = destination_id
        canonical_result = {"location": player.location, "location_name": destination.title}

        narration = self.narrate_fn(
            "move",
            canonical_result,
            world,
            {
                "actor": player.name,
                "target": target,
                "location": player.location,
                "recent_actions": [
                    entry.get("action") for entry in room_obj.player_histories.get(participant_id, [])[-3:]
                    if isinstance(entry, dict)
                ],
            },
        )

        choices = self.choice_service.build_choices(
            enemies=self.state_manager.visible_enemies(room_obj, player),
            npcs=self.state_manager.visible_npcs(room_obj, player),
            exits=self.state_manager.get_exits(room_obj, player),
        )

        return self.response_fn(
            "move",
            narration.get("text", f"Przemieszczasz się do: {player.location}"),
            canonical_result,
            world,
            choices,
        )
