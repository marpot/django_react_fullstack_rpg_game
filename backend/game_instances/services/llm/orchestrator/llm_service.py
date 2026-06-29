from game_instances.services.llm.intent.intent_parser import IntentParser
from game_instances.services.llm.narration_service.narration_service import NarrationService
from game_instances.services.llm.core.llm_client import LLMClient

class LLMService:
    """
    Orchestrator LLM system (FACADE)
    """

    def __init__(self):
        self.parser = IntentParser()
        self.narration = NarrationService()

    # -------------------------
    # INPUT → ACTION
    # -------------------------
    def parse_player_input(self, player_input: str) -> dict:
        return self.parser.parse(player_input)

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
            }
        }