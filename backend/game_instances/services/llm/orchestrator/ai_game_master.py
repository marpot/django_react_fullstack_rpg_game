import json
import logging

from game.core.game_command import GameCommand
from game_instances.services.llm.core.llm_client import LLMClient
from game_instances.services.llm.dialogue.npc_dialogue_context import NPCDialogueContextBuilder
from game_instances.services.llm.dialogue.npc_dialogue_service import NPCDialogueService
from game_instances.services.llm.intent.game_context import GameContextBuilder
from game_instances.services.llm.intent.intent_parser import IntentParser
from game_instances.services.llm.narration_service.narration_service import NarrationService
from game_instances.services.llm.narration_service.narration_context import NarrationContextBuilder

logger = logging.getLogger(__name__)


class AIGameMaster:
    """Interpret input and narrate canonical events; never execute commands."""

    def __init__(self, *, intent_client=None, narration_service=None,
                 parser=None, context_builder=None, narration_context_builder=None,
                 dialogue_service=None, dialogue_context_builder=None):
        self.intent_client = intent_client
        self.narration_service = narration_service
        self.parser = parser or IntentParser()
        self.context_builder = context_builder or GameContextBuilder()
        self.narration_context_builder = narration_context_builder or NarrationContextBuilder()
        self.dialogue_service = dialogue_service
        self.dialogue_context_builder = dialogue_context_builder or NPCDialogueContextBuilder()

    def interpret_player_input(
        self, player_input: str | dict, *, state_manager=None,
        room=None, participant_id=None,
    ) -> dict:
        parsed = self.parser.parse(player_input)
        if parsed.get("action") != "unknown":
            try:
                command = GameCommand.from_mapping(parsed)
                return self._command_mapping(command)
            except ValueError:
                pass

        unknown = {"action": "unknown", "target": None, "method": None}
        if state_manager is None or room is None or participant_id is None:
            return unknown

        context = self.context_builder.build(state_manager, room, participant_id)
        if context is None:
            return unknown

        if isinstance(player_input, str):
            message = player_input
        elif isinstance(player_input, dict):
            message = player_input.get("input") or player_input.get("message") or player_input.get("text")
        else:
            message = None
        if not isinstance(message, str) or not message.strip():
            return unknown

        system_prompt = (
            "Interpret the player's message as one game action. "
            "Use the supplied server context to identify known targets. "
            "Return only action, target and method; do not invent game state."
        )
        user_prompt = json.dumps(
            {"message": message[:1000], "game_context": context},
            ensure_ascii=False,
        )
        try:
            client = self.intent_client or LLMClient()
            candidate = json.loads(client.generate_intent(system_prompt, user_prompt))
            if not isinstance(candidate, dict) or set(candidate) != {"action", "target", "method"}:
                return unknown
            command = GameCommand.from_mapping(candidate)
        except (TypeError, ValueError):
            return unknown
        except Exception:
            logger.exception("LLM intent interpretation failed")
            return unknown

        return self._command_mapping(command)

    @staticmethod
    def _command_mapping(command: GameCommand) -> dict:
        return {
            "action": command.action,
            "target": command.target,
            "method": command.method,
        }

    def narrate_event(self, action: str, result: dict, world: dict | None = None,
                      details: dict | None = None) -> dict:
        if self.narration_service is None:
            self.narration_service = NarrationService()
        context = self.narration_context_builder.build(action, result, world, details)
        return {"text": self.narration_service.event(context)}

    def dialogue_with_npc(self, talk_result: dict, world: dict | None = None,
                          details: dict | None = None) -> str:
        context = self.dialogue_context_builder.build(talk_result, world, details)
        if self.dialogue_service is None:
            self.dialogue_service = NPCDialogueService()
        return self.dialogue_service.generate(context)
