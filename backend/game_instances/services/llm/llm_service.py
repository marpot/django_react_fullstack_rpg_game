from .intent_parser import IntentParser
from .narration_service import NarrationService
from .llm_client import LLMClient

class LLMService:
    """
    Orchestator LLM System
    """

    def __init__(self):
        self.parser = IntentParser()
        self.narration = NarrationService()
        self.client = LLMClient()


    # -------------------------
    # PLAYER INPUT → ACTION
    # -------------------------
    def parse_player_input(self, player_input: str) -> dict:
        return self.parser.parse(player_input)
    
    # -------------------------
    # INTRO STORY
    # -------------------------
    def generate_intro(self, context: dict) -> dict:
        text = self.narration.intro(context)

        return {
            "text": text
        }

    # -------------------------
    # EVENT STORY
    # -------------------------
    def generate_event_narration(self, context: dict) -> dict:
        text = self.narration.event(context)

        return {
            "text": text
        }