import json
import logging
import asyncio

from asgiref.sync import sync_to_async

from .base import BaseConsumer
from chat.models import Room, RoomParticipant
from game_instances.services.llm.orchestrator.ai_game_master import AIGameMaster
from game.core.action_processor import ActionProcessor
from game.services.game_action_service import GameActionService, NO_ACTION
from game.services.game_turn_service import GameTurnService
from game.services.bot_player_service import BotPlayerService
from game.services.bot_turn_service import BotTurnService
from game.utils.narration import normalize_narration_text

logger = logging.getLogger(__name__)


class GameConsumer(BaseConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.world = None

    async def on_connect(self):
        logger.info("=== GAME CONSUMER WS CONNECTED===")

        self.state_manager = self.scope["state_manager"]
        self.ai_game_master = AIGameMaster()
        self.processor = ActionProcessor(
            self.state_manager, narrate_fn=self.ai_game_master.narrate_event,
            dialogue_fn=self.ai_game_master.dialogue_with_npc,
        )
        self.game_action_service = GameActionService(
            self.processor,
            self.ai_game_master,
        )
        self.bot_player_service = BotPlayerService(self.state_manager)
        self.bot_turn_service = BotTurnService(
            self.state_manager,
            self.bot_player_service,
            self.processor,
        )

        self.adventure_id = None
        self.participant_id = None
        self.character_id = None

        self.room_name = str(self.room_name)
        self.room_group_name = self.get_room_group_name()

        try:
            room = await sync_to_async(
                lambda: Room.objects.select_related("adventure").get(id=self.room_name)
            )()

            self.adventure_id = getattr(room.adventure, "id", None)
            await self._resolve_participant()

            if room.state == "in_game":
                if self.state_manager.get_room(self.room_name) is not None:
                    await self._mark_connected()
                await self._send_existing_game_state()
            elif self.participant_id is not None:
                await self._mark_connected()

        except Room.DoesNotExist:
            logger.warning(f"[GAME CONSUMER] room not found: {self.room_name}")

    async def _mark_connected(self):
        await sync_to_async(
            self.state_manager.set_participant_presence
        )(self.room_name, self.participant_id, True)
        room_state = self.state_manager.get_room(self.room_name)
        if room_state is not None and room_state.current_player_id is None:
            GameTurnService(self.state_manager).advance_turn(room_state)

    async def disconnect(self, close_code):
        if (
            getattr(self, "state_manager", None) is not None
            and getattr(self, "participant_id", None) is not None
        ):
            room_state = self.state_manager.get_room(self.room_name)
            if room_state is not None:
                await sync_to_async(
                    GameTurnService(self.state_manager).mark_disconnected
                )(room_state, self.participant_id)

        await super().disconnect(close_code)

    async def _resolve_participant(self):
        """
        Resolve RoomParticipant for the authenticated user in this room.

        Returns participant_id, character_id from the database.
        Does NOT trust frontend character_id.
        """
        user = self.scope["user"]
        if not user.is_authenticated:
            logger.warning("[GAME CONSUMER] unauthenticated user")
            return

        participant = await sync_to_async(
            lambda: (
                RoomParticipant.objects
                .select_related("character")
                .filter(
                    room_id=self.room_name,
                    user=user,
                    is_ai=False,
                )
                .first()
            )
        )()

        if participant is None:
            logger.warning(
                f"[GAME CONSUMER] no participant found for user={user.id} "
                f"in room={self.room_name}"
            )
            return

        self.participant_id = participant.id
        character = participant.character

        if character is not None and character.user_id == user.id:
            self.character_id = character.id

        if self.character_id is None:
            logger.warning(
                f"[GAME CONSUMER] human participant={participant.id} "
                "has no valid owned character"
            )

    def _build_turn_state(self, room_state):
        return self.state_manager.build_turn_state(
            room_state,
            self.participant_id,
        )

    async def _build_game_state(self, room_state):
        return await sync_to_async(self.state_manager.build_game_state)(room_state)

    async def _send_existing_game_state(self):
        room_state = self.state_manager.get_room(self.room_name)

        if not room_state or not room_state.started or room_state.world is None:
            await self.send(text_data=json.dumps({
                "type": "game_event",
                "event": "error",
                "payload": {
                    "reason": "game_state_unavailable",
                    "details": "The running game state is unavailable.",
                },
                "text": "The running game state is unavailable.",
            }))
            return

        self.world = room_state.world
        self.adventure_id = room_state.adventure_id or self.adventure_id
        game_state = await self._build_game_state(room_state)

        await self.send(text_data=json.dumps({
            "type": "game_event",
            "event": "game_started",
            "payload": {
                "world": room_state.world,
                "room_id": self.room_name,
                "adventure_id": self.adventure_id,
                "turn_state": self._build_turn_state(room_state),
                "game_state": game_state,
                "reconnect": True,
            },
            "text": room_state.world.get("intro", "The adventure continues."),
        }))
        await self._run_bot_turn_if_needed()

    async def _run_bot_turn_if_needed(self):
        results = await sync_to_async(self.bot_turn_service.execute)(
            self.room_name,
            adventure=self.adventure_id,
            world=self.world,
        )
        for result in results:
            await self._broadcast_action_result(result)

    async def _broadcast_action_result(self, result):
        cleaned_text = normalize_narration_text(result.get("text", ""))
        room_state = self.state_manager.get_room(self.room_name)
        actor_id = result.pop("_actor_id", getattr(self, "participant_id", None))
        actor = room_state.players.get(actor_id) if room_state is not None else None
        await self._send_game_event(
            "action_result",
            {
                "data": result,
                "user": "bot",
                "actor": {
                    "participant_id": actor_id,
                    "name": actor.name if actor is not None else "",
                    "is_ai": actor_id in room_state.ai_participants
                    if room_state is not None
                    else False,
                },
                "text": cleaned_text,
                "turn_state": result.get("turn_state", {}) or {},
                "game_state": await self._build_game_state(room_state)
                if room_state is not None
                else {},
                "choices": result.get("choices", []),
            },
            text=cleaned_text,
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data.get("type") == "init":
                self._handle_init_message(data)
                return

            if not self._has_valid_player_input(data):
                return

            if not await self._validate_player_context():
                return

            result = await self._execute_player_action(data)
            if result is NO_ACTION:
                return

            room_state = await self._broadcast_player_action(result)
            await self._continue_with_bot_turns(room_state)

        except Exception as e:
            await self._handle_receive_error(e)

    def _handle_init_message(self, data):
        # Frontend może wysłać character_id — NIE traktujemy tego jako
        # źródła autoryzacji ani identyfikacji tury.
        # participant_id jest ustalany przez _resolve_participant() z DB.
        frontend_char_id = data.get("character_id")
        if self.participant_id is not None and self.character_id is not None:
            if frontend_char_id is not None and frontend_char_id != self.character_id:
                logger.warning(
                    f"[GAME CONSUMER] frontend character_id={frontend_char_id} "
                    f"mismatches database character_id={self.character_id}; "
                    f"ignoring frontend value"
                )

    def _has_valid_player_input(self, data):
        if "command" in data:
            return True

        user_input = data.get("message", "")
        return isinstance(user_input, str) and bool(user_input.strip())

    async def _validate_player_context(self):
        if self.participant_id is None:
            logger.warning(
                "[GAME CONSUMER] no participant_id resolved for user; "
                "rejecting action"
            )
            await self._send_game_event(
                "error",
                {
                    "reason": "no_participant",
                    "details": "Nie jesteś uczestnikiem tego pokoju.",
                },
                text="Nie jesteś uczestnikiem tego pokoju.",
            )
            return False

        if self.character_id is None:
            await self._send_game_event(
                "error",
                {
                    "reason": "no_character",
                    "details": "Wybierz postać przed rozpoczęciem rozgrywki.",
                },
                text="Wybierz postać przed rozpoczęciem rozgrywki.",
            )
            return False

        return True

    async def _execute_player_action(self, data):
        return await sync_to_async(self.game_action_service.execute)(
            data,
            state_manager=self.state_manager,
            room=self.room_name,
            participant_id=self.participant_id,
            adventure=self.adventure_id,
            world=self.world,
        )

    async def _broadcast_player_action(self, result):
        cleaned_text = normalize_narration_text(result.get("text", ""))
        turn_state = result.get("turn_state", {}) or {}
        room_state = self.state_manager.get_room(self.room_name)
        game_state = (
            await self._build_game_state(room_state)
            if room_state is not None
            else {}
        )

        payload = {
            "data": result,
            "user": self.scope["user"].username,
            "actor": {
                "participant_id": self.participant_id,
                "name": room_state.players[self.participant_id].name,
                "is_ai": self.participant_id in room_state.ai_participants,
            },
            "text": cleaned_text,
            "turn_state": turn_state,
            "game_state": game_state,
            "choices": result.get("choices", []),
        }

        await self._send_game_event(
            "action_result",
            payload,
            text=cleaned_text,
        )
        return room_state

    async def _continue_with_bot_turns(self, room_state):
        if room_state.current_player_id in room_state.ai_participants:
            await asyncio.sleep(3)
        await self._run_bot_turn_if_needed()

    async def _handle_receive_error(self, error):
        logger.error(f"GAME ERROR: {repr(error)}", exc_info=True)

        await self._send_game_event(
            "error",
            {
                "reason": "exception",
                "details": str(error),
            },
            text=str(error),
        )

    async def game_event(self, event):
        if event.get("event") == "game_started":
            payload = event.get("payload") or {}
            world = payload.get("world")
            if world:
                self.world = world
            adventure_id = payload.get("adventure_id")
            if adventure_id:
                self.adventure_id = adventure_id
            await self._run_bot_turn_if_needed()

        await super().game_event(event)

    async def game_started(self, event):
        payload = event.get("payload") or event
        await self.game_event({
            "type": "game_event",
            "event": "game_started",
            "payload": payload,
            "text": event.get("text"),
        })
