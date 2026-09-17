import logging
from copy import deepcopy

from game.core.choice_service import AdventureChoiceService
from game.core.game_command import GameCommand
from game.core.narration_fallback import narration_fallback
from game.services.combat_service import CombatService
from game.services.dice_service import DiceService
from game.state.resolver.entity_resolver import EntityResolver
from game.state.runtime.runtime_player_service import RuntimePlayerService
from game.npc.npc_service import NPCService

from game.core.actions.action_attack import AttackAction
from game.core.actions.action_move import MoveAction
from game.core.actions.action_inspect import InspectAction

logger = logging.getLogger(__name__)
_UNSET = object()


class ActionProcessor:
    def __init__(self, state_manager, combat_service=None, resolver=None,
                 narrate_fn=None, dialogue_fn=None):
        self.state_manager = state_manager
        self.narrate_fn = narrate_fn
        self.dialogue_fn = dialogue_fn
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

    def _narrate(self, action: str, result: dict, world: dict | None = None,
                 details: dict | None = None):
        fallback = {"text": narration_fallback(action, result)}
        if self.narrate_fn is None:
            return fallback
        try:
            narration = self.narrate_fn(action, deepcopy(result), world, details)
            if isinstance(narration, dict) and isinstance(narration.get("text"), str) and narration["text"].strip():
                return narration
        except Exception:
            logger.exception("Event narration failed")
        return fallback

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

    def _advance_reference_adventure(self, room_obj, participant_id, action, result):
        """Apply the small deterministic Cienie Eldorii progression slice."""
        if not room_obj.adventure_id:
            return
        try:
            from world.models import Adventure
            if not Adventure.objects.filter(
                pk=room_obj.adventure_id, title="Cienie Eldorii"
            ).exists():
                return
        except Exception:
            return

        if room_obj.quest.completed or room_obj.adventure_completed:
            return

        player = room_obj.players.get(participant_id)
        if player is None:
            return
        location = self.state_manager.get_location(room_obj, player)
        title = location.title.casefold() if location else ""
        quest = room_obj.quest

        npc_id = result.get("npc_id") or result.get("_npc_id")
        if action == "talk" and npc_id == "guard" and "village" in title:
            quest.status = "active"
            quest.stage = "forest"
            quest.objective = "Pokonaj przeciwnika w lesie"
            quest.flags["guard_spoken"] = True
        elif action == "attack" and result.get("winner") == "attacker":
            if any(enemy.hp > 0 for enemy in self.state_manager.visible_enemies(room_obj, player)):
                return
            quest.flags["enemy_defeated"] = True
            if quest.status == "active":
                quest.stage = "merchant"
                quest.objective = "Odnajdź kupca w lesie"
        elif action == "talk" and npc_id == "merchant":
            if quest.flags.get("enemy_defeated") and "forest" in title:
                quest.flags["merchant_found"] = True
                quest.stage = "return"
                quest.objective = "Wróć do wioski"
        elif action == "move" and "village" in title:
            if quest.flags.get("merchant_found"):
                quest.status = "completed"
                quest.stage = "completed"
                quest.objective = None
                quest.completed = True
                room_obj.adventure_completed = True

    def process(
        self, parsed_input, *, room=_UNSET, participant_id=_UNSET,
        adventure=_UNSET, world=_UNSET, player_message=None,
    ):
        logger.info("[ACTION PROCESS] input=%s", parsed_input)

        try:
            command = (
                parsed_input if isinstance(parsed_input, GameCommand)
                else GameCommand.from_mapping(parsed_input)
            )
        except (TypeError, ValueError):
            return self._response(
                "unknown",
                "Invalid action",
                {"error": "invalid_action"}
            )

        # Legacy callers may still pass a combined dict. Explicit server context
        # takes precedence, and only command fields reach action handlers.
        legacy = parsed_input if isinstance(parsed_input, dict) else {}
        room = legacy.get("room") if room is _UNSET else room
        participant_id = legacy.get("participant_id") if participant_id is _UNSET else participant_id
        adventure = legacy.get("adventure") if adventure is _UNSET else adventure
        world = legacy.get("world") if world is _UNSET else world
        parsed_input = {
            "action": command.action,
            "target": command.target,
            "method": command.method,
            "room": room,
            "participant_id": participant_id,
            "adventure": adventure,
            "world": world,
        }
        action = command.action

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
            player = room_obj.players[participant_id]
            talk_result = NPCService(self.state_manager).talk(
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
            result = self._response("talk", talk_result.get("text", ""), talk_result)
            # Keep the public response shape unchanged while allowing the
            # deterministic progression hook to use the resolved NPC id.
            if resolved_npc_id is not None:
                result["_progression_npc_id"] = resolved_npc_id

        else:
            return self._response(action, "Unhandled action", {"error": "unhandled_action"})

        if result.get("result", {}).get("error"):
            return result

        self._advance_reference_adventure(
            room_obj,
            participant_id,
            action,
            {**result.get("result", {}), "_npc_id": result.get("_progression_npc_id")},
        )
        result.pop("_progression_npc_id", None)

        # wspólna część (turn + history)
        self._record_history(room_obj, participant_id, action, result.get("result", {}))
        self._advance_turn(room_obj)
        result["turn_state"] = self._turn_state(room_obj, participant_id)

        return result

    def _handle_inspect(self, parsed_input, world=None):
        # fallback legacy (można później usunąć)
        return self.inspect_action.handle(parsed_input, world)
