import json
import logging

from asgiref.sync import sync_to_async

from .base import BaseConsumer
from chat.models import Room
from game_instances.services.llm.llm_service import LLMService
from game.core.action_processor import ActionProcessor
from world.seeders.world_seeder import WorldSeeder
from game.models import GameSession
from game.core.events.memory_builder import GameMemoryBuilder

logger = logging.getLogger(__name__)


class GameConsumer(BaseConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._game_started_sent = False
        self._world_sent = False

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
                "world": None
            })

            if not isinstance(parsed, dict) or "action" not in parsed:
                return

            parsed["room"] = self.room_name
            parsed["user_id"] = self.scope["user"].id
            parsed["adventure"] = self.adventure_id

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
            logger.error(f"GAME ERROR: {repr(e)}", exc_info=True)

            await self.send_event(
                "game_event",
                {
                    "subtype": "error",
                    "text": str(e)
                }
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

        await sync_to_async(self.seeder.seed_from_adventure)(
            adventure_id,
            self.room_name
        )

        llm = LLMService()

        # FIX: make LLM call async-safe (avoid blocking event loop)
        world = await sync_to_async(llm.generate_world)(
            {"adventure": {"id": adventure_id}}
        )

        if not isinstance(world, dict):
            world = {
                "intro": "A strange world forms...",
                "situation": "The world is unstable."
            }

        await self._save_world_state(world)

        if self._world_sent:
            return

        self._world_sent = True

        await self.send_event(
            "game_event",
            {
                "subtype": "world_start",
                "event": "game_started",
                "text": world.get("intro", "A new world begins..."),
                "world": world,
                "room_id": self.room_name
            }
        )

    async def game_event(self, event):
        payload = event.get("payload", None)

        if payload is not None:
            data = payload
        else:
            data = {
                k: v for k, v in event.items()
                if k != "type"
            }

        await self.send(text_data=json.dumps({
            "type": "game_event",
            **data
        }))

    @sync_to_async
    def _resolve_character(self):
        from accounts.models import PlayerCharacter

        user = self.scope.get("user")
        player = PlayerCharacter.objects.filter(user=user).first()

        if player:
            self.character_id = player.id
        else:
            logger.error("[CHARACTER RESOLVE FAILED]")

    @sync_to_async
    def _save_world_state(self, world_data: dict):
        from accounts.models import PlayerCharacter

        if not self.adventure_id:
            return

        player = PlayerCharacter.objects.filter(id=self.character_id).first()

        if not player:
            return

        session, _ = GameSession.objects.get_or_create(
            player=player,
            adventure_id=self.adventure_id,
            defaults={"progress": {}}
        )

        session.progress = {
            "world": {
                "adventure_id": self.adventure_id,
                "room_id": self.room_name,
                "state": world_data,
            }
        }

        session.save()