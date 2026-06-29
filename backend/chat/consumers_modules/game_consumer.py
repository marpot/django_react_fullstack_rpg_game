import json
import logging

from asgiref.sync import sync_to_async

from .base import BaseConsumer
from chat.models import Room
from game_instances.services.llm.orchestrator.llm_service import LLMService
from game.core.action_processor import ActionProcessor
from world.seeders.world_seeder import WorldSeeder
from game.core.events.memory_builder import GameMemoryBuilder

logger = logging.getLogger(__name__)


class GameConsumer(BaseConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._game_started_sent = False
        self._world_sent = False
        self.world = None  # 🔥 ważne

    async def on_connect(self):
        logger.info("=== GAME CONSUMER WS CONNECTED===")

        self.state_manager = self.scope["state_manager"]
        self.processor = ActionProcessor(self.state_manager)
        self.seeder = WorldSeeder(self.state_manager)

        self.adventure_id = None
        self.character_id = None

        self.room_name = str(self.room_name)
        self.room_group_name = self.get_room_group_name()

        try:
            room = await sync_to_async(
                lambda: Room.objects.select_related("adventure").get(id=self.room_name)
            )()

            self.adventure_id = getattr(room.adventure, "id", None)
            await self._resolve_character()

        except Room.DoesNotExist:
            logger.warning(f"[GAME CONSUMER] room not found: {self.room_name}")

    async def _resolve_character(self):
        self.character_id = self.scope["user"].id

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            user_input = data.get("message", "")

            if data.get("type") == "init":
                self.character_id = data.get("character_id")
                return

            if not isinstance(user_input, str) or not user_input.strip():
                return

            memory = await sync_to_async(GameMemoryBuilder().build)(
                self.adventure_id,
                self.room_name,
                20
            )

            llm = LLMService()

            parsed = llm.parse_player_input({
                "input": user_input,
                "memory": memory,
                "world": self.world
            })

            if not isinstance(parsed, dict) or "action" not in parsed:
                return

            parsed["room"] = self.room_name
            parsed["user_id"] = self.scope["user"].id
            parsed["adventure"] = self.adventure_id
            parsed["world"] = self.world  # 🔥 kluczowa zmiana

            result = await sync_to_async(self.processor.process)(parsed)

            await self._send_game_event(
                "action_result",
                {
                    "data": result,
                    "user": self.scope["user"].username,
                },
                text=result.get("text", "")
            )

        except Exception as e:
            logger.error(f"GAME ERROR: {repr(e)}", exc_info=True)

            await self._send_game_event(
                "error",
                {
                    "reason": "exception",
                    "details": str(e),
                },
                text=str(e)
            )

    async def game_started(self, event):
        if self._game_started_sent:
            return

        self._game_started_sent = True

        if event.get("payload") is not None:
            event = event["payload"]

        adventure_id = event.get("adventure_id")
        if not adventure_id:
            return

        self.adventure_id = adventure_id

        await sync_to_async(self.state_manager.get_or_create_room)(self.room_name)

        await sync_to_async(self.seeder.seed_from_adventure)(
            adventure_id,
            self.room_name
        )

        llm = LLMService()

        world_raw = await sync_to_async(llm.generate_world)(
            {"adventure": {"id": adventure_id}}
        )

        if not isinstance(world_raw, dict):
            world_raw = {
                "intro": "A strange world forms...",
                "situation": "The world is unstable."
            }

        self.world = {
            "name": world_raw.get("name", "Unknown World"),
            "title": world_raw.get("title", "Unknown World"),
            "description": world_raw.get("description", ""),
            "intro": world_raw.get("intro", ""),
            "lore": {
                "situation": world_raw.get("situation", "")
            },
            "rules": world_raw.get("rules", {}),
            "seed": world_raw.get("seed", {}),
        }

        logger.info(f"[GAME_CONSUMER] world generated: {self.world}")

        if self._world_sent:
            return

        self._world_sent = True

        await self._send_game_event(
            "game_started",
            {
                "world": self.world,
                "room_id": self.room_name,
                "adventure_id": adventure_id,
            },
            text=self.world.get("intro", "A new world begins...")
        )