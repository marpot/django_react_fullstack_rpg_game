import logging

from game.npc.npc_service import NPCService

logger = logging.getLogger(__name__)


class TalkAction:
    def __init__(self, state_manager, dialogue_fn, response_fn):
        self.state_manager = state_manager
        self.dialogue_fn = dialogue_fn
        self.response_fn = response_fn
        self.npc_service = NPCService(state_manager)

    def handle(self, parsed_input, world=None, player_message=None):
        room_obj = self.state_manager.get_or_create_room(
            self.state_manager.normalize_room_id(parsed_input["room"])
        )
        participant_id = parsed_input["participant_id"]
        player = room_obj.players[participant_id]

        talk_result = self.npc_service.talk(
            parsed_input["room"],
            parsed_input["target"],
            location=player.location,
        )

        if "error" not in talk_result and self.dialogue_fn is not None:
            details = {
                "actor": player.name,
                "location": player.location,
                "player_message": player_message,
                "recent_actions": [
                    entry.get("action")
                    for entry in room_obj.player_histories.get(participant_id, [])[-3:]
                    if isinstance(entry, dict)
                ],
            }

            try:
                dialogue = self.dialogue_fn(talk_result.copy(), world, details)
                if isinstance(dialogue, str) and dialogue.strip():
                    talk_result["text"] = dialogue.strip()
            except Exception:
                logger.exception("NPC dialogue failed")

        resolved_npc_id = talk_result.get("npc_id")
        talk_result.pop("npc_id", None)
        talk_result.pop("personality", None)

        result = self.response_fn(
            "talk",
            talk_result.get("text", ""),
            talk_result,
        )

        if resolved_npc_id is not None:
            result["_progression_npc_id"] = resolved_npc_id

        return result
