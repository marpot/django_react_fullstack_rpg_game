from unittest.mock import AsyncMock, Mock

import pytest
from django.contrib.auth import get_user_model

from accounts.models import PlayerCharacter
from chat.consumers_modules.game_consumer import GameConsumer
from chat.models import Room
from chat.services.room_participants_service import RoomParticipantsService
from game.core.action_processor import ActionProcessor
from game.services.bot_player_service import BotPlayerService
from game.services.game_start_service import GameStartService
from game.services.game_turn_service import GameTurnService
from game.state.game_state_manager import GameStateManager
from game.state.runtime.models import Player
from world.models import Adventure


def bot_room():
    state = GameStateManager()
    room = state.get_or_create_room("bot-room")
    room.ai_participants = {7}
    room.connected_participants = {8}
    room.turn_order = [7, 8]
    room.current_player_id = 7
    room.current_turn_index = 0
    room.players[7] = Player(
        id=7, name="Demo Companion", hp=100, max_hp=100,
        attack_bonus=2, damage_die=6, damage_bonus=1, defense=10,
    )
    room.players[8] = Player(
        id=8, name="Hero", hp=100, max_hp=100,
        attack_bonus=2, damage_die=6, damage_bonus=1, defense=10,
    )
    room.player_histories = {7: [], 8: []}
    return state, room


def test_bot_is_active_without_websocket_and_is_in_turn_order():
    state, room = bot_room()

    assert 7 in room.players
    assert 7 in room.turn_order
    assert GameTurnService(state).is_participant_active(room, 7)


def test_bot_command_uses_action_processor_and_advances_turn():
    state, room = bot_room()
    processor = ActionProcessor(state)

    command = BotPlayerService(state).choose_command(room, 7)
    result = processor.process(
        command,
        room=room.name,
        participant_id=7,
    )

    assert result["action"] == command.action
    assert room.player_histories[7][-1]["action"] == command.action
    assert room.current_player_id == 8


def test_bot_cannot_bypass_action_processor_validation():
    state, room = bot_room()
    processor = ActionProcessor(state)

    result = processor.process(
        {"action": "teleport"},
        room=room.name,
        participant_id=7,
    )

    assert result["result"]["error"] == "invalid_action"
    assert room.current_player_id == 7


def test_disconnected_human_does_not_block_bot_turn():
    state, room = bot_room()
    room.connected_participants = set()
    room.current_player_id = 8
    GameTurnService(state).mark_disconnected(room, 8)

    assert room.current_player_id == 7
    command = BotPlayerService(state).choose_command(room, 7)
    assert command.action in {"inspect", "move", "talk", "attack"}


@pytest.mark.django_db
def test_game_start_registers_ai_participant_in_runtime():
    user = get_user_model().objects.create_user(username="bot-start-user")
    character = PlayerCharacter.objects.create(user=user, name="Hero")
    adventure = Adventure.objects.create(title="Bot adventure", creator=user)
    room_record = Room.objects.create(
        name="bot-start-room", owner=user, adventure=adventure
    )
    RoomParticipantsService.add_human(room_record, user, character)
    bot = RoomParticipantsService.add_ai(room_record, "Demo Companion")
    state = GameStateManager()
    llm = Mock()
    llm.generate_world.return_value = {}
    llm.generate_intro.return_value = {}

    GameStartService(
        seeder=Mock(), llm=llm, notifier=Mock(), state_manager=state
    ).start_game(adventure.id, room_record.id, adventure=adventure)

    room = state.get_room(room_record.id)
    assert bot.id in room.players
    assert bot.id in room.turn_order
    assert bot.id in room.ai_participants
    assert GameTurnService(state).is_participant_active(room, bot.id)


@pytest.mark.django_db
def test_started_game_can_execute_ai_from_real_participant_flow():
    user = get_user_model().objects.create_user(username="bot-flow-user")
    character = PlayerCharacter.objects.create(user=user, name="Hero")
    adventure = Adventure.objects.create(title="Bot flow adventure", creator=user)
    room_record = Room.objects.create(
        name="bot-flow-room", owner=user, adventure=adventure
    )
    human = RoomParticipantsService.add_human(room_record, user, character)
    bot = RoomParticipantsService.add_ai(room_record, "Eldrin")
    state = GameStateManager()
    llm = Mock()
    llm.generate_world.return_value = {}
    llm.generate_intro.return_value = {}

    GameStartService(
        seeder=Mock(), llm=llm, notifier=Mock(), state_manager=state
    ).start_game(adventure.id, room_record.id, adventure=adventure)

    room = state.get_room(room_record.id)
    assert room.current_player_id == human.id
    assert GameTurnService(state).advance_turn(room) == bot.id
    assert room.current_player_id == bot.id

    consumer = object.__new__(GameConsumer)
    consumer.state_manager = state
    consumer.room_name = str(room_record.id)
    consumer.adventure_id = adventure.id
    consumer.world = room.world
    consumer.processor = ActionProcessor(state)
    consumer.bot_player_service = BotPlayerService(state)

    results = consumer._execute_bot_turns()

    assert bot.id in room.players
    assert bot.id in room.ai_participants
    assert bot.id in room.turn_order
    assert str(bot.id) in state.build_game_state(room)["players"]
    assert results and results[0]["action"] == "attack"
    assert room.player_histories[bot.id][-1]["action"] == "attack"
    assert room.current_player_id == human.id


@pytest.mark.asyncio
async def test_game_consumer_executes_bot_through_canonical_path():
    state, room = bot_room()
    consumer = object.__new__(GameConsumer)
    consumer.state_manager = state
    consumer.room_name = room.name
    consumer.adventure_id = None
    consumer.world = {}
    consumer.processor = ActionProcessor(state)
    consumer.bot_player_service = BotPlayerService(state)
    consumer._send_game_event = AsyncMock()

    results = consumer._execute_bot_turns()

    assert len(results) == 1
    assert results[0]["action"] == "attack"
    assert room.player_histories[7][-1]["action"] == "attack"
    assert room.current_player_id == 8

    await consumer._broadcast_action_result(results[0])
    event_payload = consumer._send_game_event.await_args.args[1]
    assert event_payload["data"]["action"] == "attack"
    assert event_payload["game_state"]["players"]["7"]["name"] == "Demo Companion"
    assert event_payload["game_state"]["player_histories"]["7"]


def test_several_ai_turns_have_a_bounded_execution():
    state, room = bot_room()
    room.ai_participants = {7, 8}
    room.turn_order = [7, 8]
    room.current_player_id = 7
    room.connected_participants = set()
    room.players[8].name = "Second Companion"
    consumer = object.__new__(GameConsumer)
    consumer.state_manager = state
    consumer.room_name = room.name
    consumer.adventure_id = None
    consumer.world = {}
    consumer.processor = ActionProcessor(state)
    consumer.bot_player_service = BotPlayerService(state)

    results = consumer._execute_bot_turns()

    assert len(results) == len(room.turn_order)
    assert len(room.player_histories[7]) == 1
    assert len(room.player_histories[8]) == 1
