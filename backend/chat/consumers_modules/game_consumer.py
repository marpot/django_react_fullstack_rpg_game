import json
import traceback

from world.seeders.world_seeder import WorldSeeder
from asgiref.sync import sync_to_async

from .base import BaseConsumer
from game_instances.services.llm.llm_service import LLMService
from game.state.game_state_manager import GameStateManager
from game.core.action_processor import ActionProcessor


class GameConsumer(BaseConsumer):

    async def on_connect(self):
        print("=== GAME CONSUMER WS CONNECTED===")
        print("ROOM DEBUG:", self.room_name)

        self.state_manager = GameStateManager()
        self.processor = ActionProcessor(self.state_manager)

    async def receive(self, text_data):
        print("=== GAME RECEIVE START ===")

        try:
            data = json.loads(text_data)
            user_input = data.get("message", "").strip()

            if not user_input:
                return

            llm = LLMService()
            parsed = llm.parse_player_input(user_input)

            parsed["room"] = self.room_name
            parsed["user_id"] = self.scope["user"].id

            result = await sync_to_async(self.processor.process)(parsed)

            await self.send_event(
                "game_event",
                {
                    "subtype": "action_result",
                    "text": result.get("text", str(result)),
                    "data": result,
                    "user": self.scope["user"].username
                }
            )

        except Exception as e:
            print("GAME ERROR:", repr(e))
            traceback.print_exc()

            await self.send_event(
                "game_event",
                {
                    "subtype": "error",
                    "text": str(e)
                }
            )

    async def game_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "game_event",
            **event["payload"]
        }))

    async def game_started(self, event):
        adventure_id = event.get("adventure_id")

        if not adventure_id:
            await self.send_event(
                "game_event",
                {
                    "subtype": "error",
                    "text": "Cannot start game without adventure selected",
                    "event": "game_started_failed"
                }
            )
            return

        seeder = WorldSeeder(self.state_manager)

        await sync_to_async(seeder.seed_from_adventure)(
            adventure_id,
            self.room_name
        )

        await self.send_event(
            "game_event",
            {
                "subtype": "system",
                "text": event.get("message", "Game started"),
                "room_id": self.room_name,
                "event": "game_started",
                "mode": "adventure"
            }
        )