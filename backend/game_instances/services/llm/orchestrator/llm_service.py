import json
import logging

from game.core.game_command import GameCommand
from game_instances.services.llm.intent.game_context import GameContextBuilder
from game_instances.services.llm.intent.intent_parser import IntentParser
from game_instances.services.llm.narration_service.narration_service import NarrationService
from game_instances.services.llm.core.llm_client import LLMClient

logger = logging.getLogger(__name__)


class LLMService:
    """
    Orchestrator LLM system (FACADE)
    """

    def __init__(self, intent_client=None):
        self.parser = IntentParser()
        self.narration = NarrationService()
        self.intent_client = intent_client
        self.context_builder = GameContextBuilder()

    # -------------------------
    # INPUT → ACTION
    # -------------------------
    def parse_player_input(
        self, player_input: str | dict, *, state_manager=None,
        room=None, participant_id=None,
    ) -> dict:
        parsed = self.parser.parse(player_input)
        if parsed.get("action") != "unknown":
            try:
                GameCommand.from_mapping(parsed)
                return parsed
            except ValueError:
                pass

        unknown = {"action": "unknown", "target": None, "method": None}
        if state_manager is None or room is None or participant_id is None:
            return unknown

        context = self.context_builder.build(state_manager, room, participant_id)
        if context is None:
            return unknown

        if isinstance(player_input, str):
            text = player_input
        elif isinstance(player_input, dict):
            text = player_input.get("input") or player_input.get("message") or player_input.get("text")
        else:
            text = None
        if not isinstance(text, str) or not text.strip():
            return unknown

        system_prompt = (
            "Interpret the player's message as one game action. "
            "Use the supplied server context to identify known targets. "
            "Return only action, target and method; do not invent game state."
        )
        user_prompt = json.dumps(
            {"message": text[:1000], "game_context": context},
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

        return {
            "action": command.action,
            "target": command.target,
            "method": command.method,
        }

    # -------------------------
    # INTRO STORY
    # -------------------------
    def generate_intro(self, context: dict) -> dict:
        return {"text": self.narration.intro(context)}

    # -------------------------
    # EVENT STORY
    # -------------------------
    def generate_event_narration(self, context: dict) -> dict:
        return {"text": self.narration.event(context)}

    # -------------------------
    # WORLD (STATIC DTO)
    # -------------------------
    def generate_world(self, context: dict) -> dict:
        adventure = context.get("adventure", {})

        title = adventure.get("title", "Unknown World")
        description = adventure.get("description", "A strange and mysterious land.")

        return {
            "name": title,
            "title": title,
            "description": description,
            "intro": f"Wkraczasz do {title}, krainy pełnej niebezpieczeństw i tajemnic.",
            "situation": "Powietrze jest ciężkie. Świat reaguje na twoją obecność.",
            "rules": {
                "danger_level": "medium",
                "npc_enabled": True,
                "combat_enabled": True
            },
            "seed": {
                "theme": "dark fantasy",
                "tone": "grim",
                "starting_state": "lobby_to_world_transition"
            },
            "choices": [
                {
                    "id": "inspect",
                    "label": "Rozejrzyj się",
                    "title": "Rozejrzyj się",
                    "description": "Sprawdź otoczenie i ślady przygody.",
                    "message": "sprawdź otoczenie",
                    "action": "inspect",
                    "target": None,
                },
                {
                    "id": "move",
                    "label": "Idź dalej",
                    "title": "Idź dalej",
                    "description": "Przejdź do kolejnego miejsca w przygodzie.",
                    "message": "idź dalej",
                    "action": "move",
                    "target": None,
                }
            ]
        }
