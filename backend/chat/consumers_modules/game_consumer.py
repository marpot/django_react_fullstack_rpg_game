import json
import logging
import re
import asyncio

from asgiref.sync import sync_to_async

from .base import BaseConsumer
from chat.models import Room, RoomParticipant
from game_instances.services.llm.orchestrator.ai_game_master import AIGameMaster
from game.core.action_processor import ActionProcessor
from game.services.game_turn_service import GameTurnService
from game.services.bot_player_service import BotPlayerService

logger = logging.getLogger(__name__)


def safe_text(text: any) -> str:
    """Radzi sobie z czystym JSON-em zwracanym przez LLM."""
    if not text:
        return "Nic się nie stało..."

    if isinstance(text, (dict, list)):
        text = json.dumps(text, ensure_ascii=False)

    if not isinstance(text, str):
        return str(text)

    original_text = text.strip()
    text = re.sub(r'```(?:json)?\s*|\s*```', '', original_text).strip()

    if text.startswith(('{' , '[')) or ('"action"' in text or '"target"' in text or '"method"' in text):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                for key in ["text", "narration", "description", "content", "story", "message", "response"]:
                    if key in parsed and isinstance(parsed[key], str) and len(parsed[key].strip()) > 5:
                        return parsed[key].strip()

                action = parsed.get("action")
                target = parsed.get("target")
                method = parsed.get("method")

                if action == "attack":
                    if target:
                        method_part = f" {method}" if method else ""
                        return f"Atakujesz {target}{method_part}."
                    return "Wykonujesz atak."
                if action == "move":
                    target_name = target or "nowego miejsca"
                    return f"Przemieszczasz się do {target_name}."
                if action in {"inspect", "look"}:
                    return "Rozglądasz się uważnie po okolicy."
                return original_text
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    try:
        match = re.search(r'(\{[\s\S]*?\})', original_text)
        if match:
            parsed = json.loads(match.group(1))
            if isinstance(parsed, dict):
                for key in ["text", "narration", "description"]:
                    if key in parsed and isinstance(parsed[key], str) and len(parsed[key]) > 5:
                        return parsed[key].strip()
    except Exception:
        pass

    return original_text


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
        self.bot_player_service = BotPlayerService(self.state_manager)

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
        results = await sync_to_async(self._execute_bot_turns)()
        for result in results:
            await self._broadcast_action_result(result)

    def _execute_bot_turns(self):
        results = []
        room_state = self.state_manager.get_room(self.room_name)
        if room_state is None:
            return results

        with self.state_manager.start_lock:
            for _ in range(len(room_state.turn_order)):
                if room_state.adventure_completed or room_state.quest.completed:
                    break

                participant_id = room_state.current_player_id
                if participant_id not in room_state.ai_participants:
                    break

                command = self.bot_player_service.choose_command(
                    room_state,
                    participant_id,
                )
                result = self.processor.process(
                    command,
                    room=self.room_name,
                    participant_id=participant_id,
                    adventure=self.adventure_id,
                    world=self.world,
                )
                result["_actor_id"] = participant_id
                results.append(result)

        return results

    async def _broadcast_action_result(self, result):
        cleaned_text = safe_text(result.get("text", ""))
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
                return

            has_command = "command" in data
            if not has_command:
                user_input = data.get("message", "")
                if not isinstance(user_input, str) or not user_input.strip():
                    return

            if self.participant_id is None:
                logger.warning(
                    "[GAME CONSUMER] no participant_id resolved for user; "
                    "rejecting action"
                )
                await self._send_game_event(
                    "error",
                    {"reason": "no_participant", "details": "Nie jesteś uczestnikiem tego pokoju."},
                    text="Nie jesteś uczestnikiem tego pokoju.",
                )
                return

            if self.character_id is None:
                await self._send_game_event(
                    "error",
                    {
                        "reason": "no_character",
                        "details": "Wybierz postać przed rozpoczęciem rozgrywki.",
                    },
                    text="Wybierz postać przed rozpoczęciem rozgrywki.",
                )
                return

            if has_command:
                parsed = data["command"]
            else:
                parsed = await sync_to_async(self.ai_game_master.interpret_player_input)(
                    {"input": user_input},
                    state_manager=self.state_manager,
                    room=self.room_name,
                    participant_id=self.participant_id,
                )

                if not isinstance(parsed, dict) or "action" not in parsed:
                    return

            result = await sync_to_async(self.processor.process)(
                parsed,
                room=self.room_name,
                participant_id=self.participant_id,
                adventure=self.adventure_id,
                world=self.world,
                player_message=None if has_command else user_input,
            )
            cleaned_text = safe_text(result.get("text", ""))

            turn_state = result.get("turn_state", {}) or {}

            room_state = self.state_manager.get_room(self.room_name)
            game_state = await self._build_game_state(room_state) if room_state is not None else {}

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
                text=cleaned_text
            )
            if room_state.current_player_id in room_state.ai_participants:
                await asyncio.sleep(3)
            await self._run_bot_turn_if_needed()

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
