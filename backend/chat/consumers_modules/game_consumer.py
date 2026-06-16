import json
import logging

from asgiref.sync import sync_to_async

from .base import BaseConsumer
from chat.models import Room
from game_instances.services.llm.llm_service import LLMService
from game.core.action_processor import ActionProcessor
from world.seeders.world_seeder import WorldSeeder

from game.models import GameSession

logger = logging.getLogger(__name__)


class GameConsumer(BaseConsumer):

    async def on_connect(self):
        logger.info("=== GAME CONSUMER WS CONNECTED===")
        logger.info(f"ROOM DEBUG: {self.room_name}")

        self.state_manager = self.scope["state_manager"]

        self.processor = ActionProcessor(self.state_manager)
        self.seeder = WorldSeeder(self.state_manager)

        self.adventure_id = None
        self.character_id = None

        self.room_name = str(self.room_name)
        self.group_name = f"gameconsumer_{self.room_name}"

        logger.info(f"GROUP NAME: {self.group_name}")

        try:
            room = await sync_to_async(
                lambda: Room.objects.select_related("adventure").get(id=self.room_name)
            )()

            self.adventure_id = getattr(room.adventure, "id", None)

            logger.info(f"[DEBUG USER] {self.scope.get('user')}")
            logger.info(f"[DEBUG USER TYPE] {type(self.scope.get('user'))}")

            player = getattr(self.scope.get("user"), "playercharacter", None)
            logger.info(f"[DEBUG PLAYER CHARACTER] {player}")

            logger.info(
                f"[GAME CONSUMER] loaded adventure_id={self.adventure_id} "
                f"for room={self.room_name}"
            )

            await self._resolve_character()

        except Room.DoesNotExist:
            logger.warning(f"[GAME CONSUMER] room not found in DB: {self.room_name}")

    # =========================
    # RECEIVE (MAIN GAME LOOP)
    # =========================
    async def receive(self, text_data):
        logger.info("=== GAME RECEIVE START ===")

        try:
            data = json.loads(text_data)

            user_input = data.get("message", "")

            if data.get("type") == "init":
                self.character_id = data.get("character_id")
                logger.info(f"[INIT] character_id={self.character_id}")
                return

            if not isinstance(user_input, str):
                logger.error(f"[INVALID INPUT TYPE] {user_input}")
                return

            user_input = user_input.strip()
            if not user_input:
                logger.warning("[EMPTY INPUT]")
                return

            llm = LLMService()
            parsed = llm.parse_player_input(user_input)

            if not isinstance(parsed, dict):
                logger.error(f"[LLM PARSE NOT DICT] {parsed}")
                return

            if "action" not in parsed:
                logger.error(f"[LLM PARSE MISSING ACTION] {parsed}")
                return

            parsed.setdefault("target", None)
            parsed.setdefault("method", None)

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

    # =========================
    # GAME EVENTS
    # =========================
    async def game_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "game_event",
            **event["payload"]
        }))

    # =========================
    # GAME START FLOW
    # =========================
    async def game_started(self, event):
        logger.info("🔥 GAME_STARTED RECEIVED IN CONSUMER")
        logger.info(f"EVENT: {event}")

        adventure_id = event.get("adventure_id")

        if not adventure_id:
            await self.send_event(
                "game_event",
                {
                    "subtype": "error",
                    "text": "Missing adventure_id",
                    "event": "game_started_failed"
                }
            )
            return

        self.adventure_id = adventure_id

        await sync_to_async(self.seeder.seed_from_adventure)(
            adventure_id,
            self.room_name
        )

        logger.info(f"[GAME START] seed complete room={self.room_name}")

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

        llm = LLMService()

        world = llm.generate_world({
            "adventure": {"id": adventure_id},
        })

        if not isinstance(world, dict):
            logger.error(f"[WORLD GENERATION FAILED] {world}")
            world = {
                "intro": "A strange world forms...",
                "situation": "The world is unstable."
            }

        room = self.state_manager.get_or_create_room(self.room_name)
        room.world = world

        await self._save_world_state(world)   # <-- PERSISTENCJA

        await self.send_event(
            "game_event",
            {
                "subtype": "world_start",
                "text": world.get("intro", "A new world begins..."),
                "world": world,
                "room_id": self.room_name,
                "event": "world_start"
            }
        )
    @sync_to_async
    def _resolve_character(self):
        from accounts.models import PlayerCharacter

        user = self.scope.get("user")

        player = PlayerCharacter.objects.filter(user=user).first()

        if player:
            self.character_id = player.id
            logger.info(f"[CHARACTER RESOLVED] id={self.character_id}")
        else:
            logger.error("[CHARACTER RESOLVE FAILED]")
    # =========================
    # PERSISTENCE HELPER
    # =========================
    @sync_to_async
    def _save_world_state(self, world_data: dict):
        from accounts.models import PlayerCharacter

        player = PlayerCharacter.objects.filter(
            id=self.character_id
        ).first()

        if not player:
            logger.error(f"[WORLD SAVE FAILED] No PlayerCharacter id={self.character_id}")
            return

        session, _ = GameSession.objects.get_or_create(
            player=player,
            defaults={"progress": {}}
        )

        progress = session.progress or {}

        progress["world"] = {
            "adventure_id": self.adventure_id,
            "room_id": self.room_name,
            "state": world_data,
        }

        session.progress = progress
        session.save()

        logger.info(f"[WORLD SAVED] session_id={session.id}")