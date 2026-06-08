import json
import traceback

from asgiref.sync import sync_to_async

from .base import BaseConsumer
from game_instances.services.llm.llm_service import LLMService
from game.state.game_state_manager import GameStateManager
from game.core.action_processor import ActionProcessor


class GameConsumer(BaseConsumer):

    async def on_connect(self):
        print("=== GAME CONSUMER WS CONNECTED===")
        print("ROOM NAME:", self.room_name)
        print("GROUP:", self.room_group_name)

        self.state_manager = GameStateManager()
        self.processor = ActionProcessor(self.state_manager)

    # =====================================================
    # GAME INPUT FLOW (player actions)
    # =====================================================
    async def receive(self, text_data):
        print("=== GAME RECEIVE START ===")
        print("RAW:", text_data)

        try:
            data = json.loads(text_data)
            print("JSON:", data)

            user_input = data.get("message", "")
            if not user_input:
                return

            llm = LLMService()
            parsed = llm.parse_player_input(user_input)

            print("LLM Result:", parsed)

            parsed["room"] = self.room_name
            parsed["user_id"] = self.scope["user"].id

            result = await sync_to_async(self.processor.process)(parsed)

            await self.send_message(
                json.dumps({
                    "type": "action_result",
                    "data": result,
                    "user": self.scope["user"].username
                })
            )

        except Exception as e:
            print("GAME ERROR:", repr(e))
            traceback.print_exc()

            await self.send_error_message(str(e))

    # =====================================================
    # GAME SYSTEM EVENT FLOW (start game broadcast)
    # =====================================================
    async def game_started(self, event):
        print("=== GAME STARTED EVENT ===", event)

        await self.send_message(json.dumps({
            "type": "game_started",
            "room_id": event.get("room_id"),
            "message": event.get("message", "Game started")
        }))