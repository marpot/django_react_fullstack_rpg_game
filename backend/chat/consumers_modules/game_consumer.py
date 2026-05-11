import json
from .base import BaseConsumer
from game_instances.services.llm.llm_service import LLMService


class GameConsumer(BaseConsumer):
    async def receive(self, text_data):
        print("=== GAME RECEIVE START ===")
        print("RAW:", text_data)

        try:
            data = json.loads(text_data)
            print("JSON:", data)

            user_input = data.get("message", "")
            if not user_input:
                return

            # 1. LLM - intent parsing
            llm = LLMService()
            parsed = llm.parse_player_input(user_input)

            print("LLM Result:", parsed)

            # ===============================
            # COMBAT SYSTEM (TEMP DISABLED)
            # ===============================
            """
            if parsed["action"] == "attack":
                attacker = SimplePlayer()
                defender = SimpleEnemy()

                combat = CombatService(DiceService())
                result = combat.resolve(attacker, defender)

                await self.send_message(str(result), username)
            """
            # ===============================


            # 2. NA RAZIE TYLKO OUTPUT (bez combat, bez modeli)
            await self.send_message(
                str(parsed),
                self.scope["user"].username
            )

        except Exception as e:
            print("GAME ERROR:", e)
            await self.send_error_message(str(e))