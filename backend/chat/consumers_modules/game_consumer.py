import json
from .base import BaseConsumer
from game_instances.services.llm.llm_service import LLMService
from game.core.game_engine import GameEngine

class GameConsumer(BaseConsumer):
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            user_input = data.get("message", "")

            if not user_input:
                return
            
            # 1. LLM - intent parsing
            llm = LLMService()
            parsed = llm.parse_player_input(user_input)

            # 2. Game engine
            # (na razie placeholder state)
            state = {
                "enemy": {
                    "goblin": {"hp": 30}
                }
            }

            engine = GameEngine(state)
            result = engine.process(parsed)
            
        except Exception as e:
            await self.send_error_message(str(e))
