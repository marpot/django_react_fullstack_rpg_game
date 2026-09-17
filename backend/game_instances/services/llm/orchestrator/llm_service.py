from game_instances.services.llm.orchestrator.ai_game_master import AIGameMaster
from game_instances.services.llm.narration_service.narration_service import NarrationService


class LLMService:
    """
    Orchestrator LLM system (FACADE)
    """

    def __init__(self, intent_client=None):
        self.narration = NarrationService()
        self.game_master = AIGameMaster(
            intent_client=intent_client, narration_service=self.narration,
        )

    # -------------------------
    # INPUT → ACTION
    # -------------------------
    def parse_player_input(
        self, player_input: str | dict, *, state_manager=None,
        room=None, participant_id=None,
    ) -> dict:
        return self.game_master.interpret_player_input(
            player_input, state_manager=state_manager,
            room=room, participant_id=participant_id,
        )

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
