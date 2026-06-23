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

            await self._send_game_event(
                "action_result",
                {
                    "data": result,
                    "user": self.scope["user"].username,
                },
                text=result.get("text", str(result))
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

        # ensure the room state exists before seeding and before generating world
        await sync_to_async(self.state_manager.get_or_create_room)(self.room_name)

        await sync_to_async(self.seeder.seed_from_adventure)(
            adventure_id,
            self.room_name
        )

        llm = LLMService()

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

        await self._send_game_event(
            "game_started",
            {
                "world": world,
                "room_id": self.room_name,
                "adventure_id": adventure_id,
            },
            text=world.get("intro", "A new world begins...")
        )

    async def _send_game_event(self, event_name: str, payload: dict | None = None, text: str | None = None):
        payload = payload or {}

        if text is not None:
            payload["text"] = text

        payload["event"] = event_name

        await self.send_event("game_event", payload)

    async def game_event(self, event):
        payload = event.get("payload") or {}
        const_event = payload.get("event") or event.get("event") or "unknown"
        text = payload.get("text") or event.get("text")

        clean_payload = {
            k: v
            for k, v in payload.items()
            if k not in {"text", "event"}
        }

        output = {
            "type": "game_event",
            "event": const_event,
            "payload": clean_payload,
        }

        if isinstance(text, str) and text:
            output["text"] = text

        await self.send(text_data=json.dumps(output))

    @sync_to_async
    def _resolve_character(self):
        from accounts.models import PlayerCharacter
        from game.state.runtime.models import Player as RuntimePlayer

        user = self.scope.get("user")
        player = PlayerCharacter.objects.filter(user=user).first()

        if player:
            self.character_id = player.id

            room = self.state_manager.get_or_create_room(self.room_name)
            runtime_player = RuntimePlayer(
                id=player.user_id,
                name=player.name,
                hp=player.health,
                max_hp=player.health,
                attack_bonus=getattr(player, "attack_bonus", 0),
                damage_die=getattr(player, "damage_die", 6),
                damage_bonus=getattr(player, "damage_bonus", 0),
                defense=getattr(player, "defense", 0),
            )

            room.players[player.user_id] = runtime_player
            room.players[str(player.user_id)] = runtime_player
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