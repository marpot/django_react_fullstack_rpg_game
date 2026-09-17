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

        player = self.runtime_player_service.get_or_create(room_obj, participant_id)

        if player is None:
            return self.response_fn("inspect", "Brak postaci", {"error": "no_player"})

        location = self.state_manager.get_location(room_obj, player)
        enemies = self.state_manager.visible_enemies(room_obj, player)
        npcs = self.state_manager.visible_npcs(room_obj, player)
        exits = self.state_manager.get_exits(room_obj, player)
        canonical_result = {
            "room": room_key,
            "location": player.location,
            "location_name": location.title if location else player.location,
            "description": location.description if location else "",
            "enemies": sorted({enemy.name for enemy in enemies.values()}),
            "npcs": [{"id": npc.id, "name": npc.name} for npc in npcs.values()],
            "exits": [{"id": choice.next_location_id,
                       "title": choice.next_location.title} for choice in exits],
        }

        narration = self.narrate_fn(
            "inspect",
            canonical_result,
            world,
            {
                "actor": player.name if player else None,
                "target": parsed_input.get("target"),
                "location": player.location if player else None,
                "recent_actions": [
                    entry.get("action") for entry in room_obj.player_histories.get(participant_id, [])[-3:]
                    if isinstance(entry, dict)
                ],
            },
        )

        choices = self.choice_service.build_choices(
            enemies=enemies,
            npcs=npcs,
            exits=exits,
        )

        return self.response_fn(
            "inspect",
            narration.get("text", "Rozglądasz się po okolicy"),
            canonical_result,
            world,
            choices,
        )
