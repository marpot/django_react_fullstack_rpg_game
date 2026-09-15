import logging

from game.core.choice_service import AdventureChoiceService
from game.services.combat_service import CombatService
from game.services.dice_service import DiceService
from game.state.resolver.entity_resolver import EntityResolver
from game.state.runtime.runtime_player_service import RuntimePlayerService
from game_instances.services.llm.orchestrator.llm_service import LLMService
from game.npc.npc_service import NPCService

from game.core.actions.action_attack import AttackAction
from game.core.actions.action_move import MoveAction
from game.core.actions.action_inspect import InspectAction

logger = logging.getLogger(__name__)


class ActionProcessor:
    def __init__(self, state_manager, combat_service=None, resolver=None):
        self.state_manager = state_manager
        self.combat_service = combat_service or CombatService(DiceService())
        self.resolver = resolver or EntityResolver(state_manager)

        self.runtime_player_service = RuntimePlayerService(state_manager)
        self.choice_service = AdventureChoiceService()

        self.attack_action = AttackAction(
            state_manager=self.state_manager,
            combat_service=self.combat_service,
            resolver=self.resolver,
            runtime_player_service=self.runtime_player_service,
            choice_service=self.choice_service,
            narrate_fn=self._narrate,
            response_fn=self._response,
        )

        self.move_action = MoveAction(
            state_manager=self.state_manager,
            resolver=self.resolver,
            runtime_player_service=self.runtime_player_service,
            choice_service=self.choice_service,
            narrate_fn=self._narrate,
            response_fn=self._response,
        )

        self.inspect_action = InspectAction(
            state_manager=self.state_manager,
            runtime_player_service=self.runtime_player_service,
            choice_service=self.choice_service,
            narrate_fn=self._narrate,
            response_fn=self._response,
        )

    def _response(self, event_type: str, text: str, result=None, world=None, choices=None, turn_state=None):
        return {
            "action": event_type,
            "event_type": event_type,
            "text": text,
            "result": result or {},
            "world": world or {},
            "choices": choices or [],
            "turn_state": turn_state or {},
        }

    def _narrate(self, action: str, result: dict, world: dict | None = None):
        llm = LLMService()
        return llm.generate_event_narration({
            "event_type": action,
            "result": result,
            "world": world or {}
        })

    def _advance_turn(self, room_obj):
        current_index = room_obj.turn_order.index(room_obj.current_player_id)
        next_index = (current_index + 1) % len(room_obj.turn_order)

        room_obj.current_player_id = room_obj.turn_order[next_index]
        room_obj.current_turn_index = next_index

        return room_obj.current_player_id

    def _record_history(self, room_obj, participant_id, action, result):
        if participant_id not in room_obj.player_histories:
            room_obj.player_histories[participant_id] = []

        room_obj.player_histories[participant_id].append({
            "action": action,
            "result": result,
            "timestamp": len(room_obj.player_histories[participant_id]),
        })

    def _turn_state(self, room_obj, participant_id):
        return {
            "current_player_id": room_obj.current_player_id,
            "current_turn_index": room_obj.current_turn_index,
            "turn_order": room_obj.turn_order,
            "is_your_turn": room_obj.current_player_id == participant_id,
            "history": room_obj.player_histories.get(participant_id, []),
        }

    def process(self, parsed_input):
        logger.info(f"[ACTION PROCESS] input={parsed_input}")

        action = parsed_input.get("action")
        world = parsed_input.get("world")

        if parsed_input.get("error") == "unknown_intent_fallback":
            action = "inspect"
            parsed_input = {**parsed_input, "action": action}

        if not action or action == "unknown":
            return self._response(
                "unknown",
                "Invalid action",
                {"error": "invalid_action"}
            )

        room = parsed_input.get("room")
        participant_id = parsed_input.get("participant_id")

        if participant_id is None:
            return self._response(
                "error",
                "Participant identity is required",
                {"error": "missing_participant_id"},
            )

        room_obj = self.state_manager.get_or_create_room(
            self.state_manager.normalize_room_id(room)
        )

        if (
            participant_id not in room_obj.players
            or participant_id not in room_obj.turn_order
        ):
            return self._response(
                "error",
                "Participant is not part of the active game",
                {
                    "error": "participant_not_in_game",
                    "turn_state": self._turn_state(room_obj, participant_id),
                },
            )

        if (
            room_obj.current_player_id is None
            or room_obj.current_player_id not in room_obj.turn_order
        ):
            return self._response(
                "error",
                "Active game has an invalid turn state",
                {
                    "error": "invalid_turn_state",
                    "turn_state": self._turn_state(room_obj, participant_id),
                },
            )

        if room_obj.current_player_id != participant_id:
            return self._response(
                "error",
                "It is not this participant's turn",
                {
                    "error": "not_your_turn",
                    "turn_state": self._turn_state(room_obj, participant_id),
                },
            )

        if action == "attack":
            result = self.attack_action.handle(parsed_input, world)

        elif action == "inspect":
            result = self.inspect_action.handle(parsed_input, world)

        elif action == "move":
            result = self.move_action.handle(parsed_input, world)

        elif action == "look":
            result = self._handle_inspect(parsed_input, world)

        elif action == "talk":
            result = NPCService(self.state_manager).talk(
                parsed_input["room"],
                parsed_input["target"]
            )
            return self._response("talk", result.get("text", ""), result)

        else:
            return self._response(action, "Unhandled action", {"error": "unhandled_action"})

        # wspólna część (turn + history)
        self._record_history(room_obj, participant_id, action, result.get("result", {}))
        self._advance_turn(room_obj)
        result["turn_state"] = self._turn_state(room_obj, participant_id)

        return result

    def _handle_inspect(self, parsed_input, world=None):
        # fallback legacy (można później usunąć)
        return self.inspect_action.handle(parsed_input, world)
