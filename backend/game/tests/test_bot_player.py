import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from django.contrib.auth import get_user_model

from accounts.models import PlayerCharacter
from chat.consumers_modules.game_consumer import GameConsumer
from chat.models import Room
from chat.services.room_participants_service import RoomParticipantsService
from game.core.action_processor import ActionProcessor
from game.domain.adventure_definition import ProgressionStep
from game.services.bot_player_service import BotPlayerService
from game.services.game_start_service import GameStartService
from game.services.game_turn_service import GameTurnService
from game.state.game_state_manager import GameStateManager
from game.state.runtime.models import Enemy as RuntimeEnemy, Player
from game.npc.npc_models import NPC
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


class RecordingChannelLayer:
    def __init__(self):
        self.events = []

    async def group_send(self, group, event):
        self.events.append(event)


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


def test_completed_adventure_stops_bot_actions():
    state, room = bot_room()
    room.adventure_completed = True
    room.quest.completed = True

    assert BotPlayerService(state).choose_command(room, 7) is None


def test_bot_attacks_only_a_living_visible_enemy():
    state, room = bot_room()
    room.adventure_id = None
    room.players[7].location = "forest"
    room.enemies["wolf"] = RuntimeEnemy(
        id="wolf",
        name="wolf",
        hp=30,
        defense=10,
        attack_bonus=2,
        damage_die=6,
        damage_bonus=1,
        location="forest",
    )
    state.get_exits = Mock(return_value=[])

    command = BotPlayerService(state).choose_command(room, 7)

    assert command.action == "attack"
    assert command.target == "wolf"


def test_bot_does_not_choose_npc_outside_current_location():
    state, room = bot_room()
    room.adventure_id = None
    room.players[7].location = "village"
    room.npcs["guard"] = NPC(
        id="guard",
        name="Guard",
        location="forest",
    )
    state.get_exits = Mock(
        return_value=[SimpleNamespace(next_location_id=2)]
    )

    command = BotPlayerService(state).choose_command(room, 7)

    assert command.action == "move"
    assert command.target == "2"


def test_bot_uses_progression_step_after_stage_changes():
    state, room = bot_room()
    room.adventure_id = 42
    room.quest.status = "active"
    room.quest.stage = "forest"
    room.quest.objective = "Find the merchant."
    definition = SimpleNamespace(
        progression=SimpleNamespace(
            steps=(
                ProgressionStep(
                    "forest", "talk:guard@Village", "Go forest", "merchant"
                ),
                ProgressionStep(
                    "merchant", "talk:merchant@Forest", "", None
                ),
            )
        )
    )
    state.visible_enemies = Mock(return_value={})
    state.visible_npcs = Mock(return_value={"merchant": object()})
    state.get_exits = Mock(return_value=[])

    with patch(
        "game.services.bot_player_service.build_definition_for_adventure",
        return_value=definition,
    ):
        command = BotPlayerService(state).choose_command(room, 7)

    assert command.action == "talk"
    assert command.target == "merchant"


def test_bot_moves_only_through_an_existing_exit_toward_progression_target():
    state, room = bot_room()
    room.adventure_id = 42
    room.quest.status = "not_started"
    definition = SimpleNamespace(
        progression=SimpleNamespace(
            steps=(
                ProgressionStep(
                    "forest", "talk:guard@Forest", "", None
                ),
            )
        )
    )
    state.visible_enemies = Mock(return_value={})
    state.visible_npcs = Mock(return_value={})
    state.get_exits = Mock(
        return_value=[
            SimpleNamespace(
                next_location_id=2,
                next_location=SimpleNamespace(title="Forest"),
            )
        ]
    )

    with patch(
        "game.services.bot_player_service.build_definition_for_adventure",
        return_value=definition,
    ):
        command = BotPlayerService(state).choose_command(room, 7)

    assert command.action == "move"
    assert command.target == "2"


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
    consumer.channel_layer = RecordingChannelLayer()
    consumer.room_group_name = "game_bot-room"

    results = consumer._execute_bot_turns()

    assert len(results) == 1
    assert results[0]["action"] == "attack"
    assert room.player_histories[7][-1]["action"] == "attack"
    assert room.current_player_id == 8

    await consumer._broadcast_action_result(results[0])
    event = consumer.channel_layer.events[0]
    event_payload = event["payload"]
    assert event_payload["data"]["action"] == "attack"
    assert event_payload["actor"] == {
        "participant_id": 7,
        "name": "Demo Companion",
        "is_ai": True,
    }
    assert event_payload["game_state"]["players"]["7"]["name"] == "Demo Companion"
    assert event_payload["game_state"]["player_histories"]["7"]

    consumer.send = AsyncMock()
    await consumer.game_event(event)
    wire_event = json.loads(consumer.send.await_args.kwargs["text_data"])
    assert wire_event["payload"]["actor"] == event_payload["actor"]


@pytest.mark.asyncio
async def test_human_action_and_following_bot_action_have_actor_metadata():
    state, room = bot_room()
    room.current_player_id = 8
    consumer = object.__new__(GameConsumer)
    consumer.state_manager = state
    consumer.room_name = room.name
    consumer.adventure_id = None
    consumer.world = {}
    consumer.participant_id = 8
    consumer.character_id = 1
    consumer.scope = {"user": Mock(username="Hero")}
    consumer.processor = ActionProcessor(state)
    consumer.bot_player_service = BotPlayerService(state)
    consumer.ai_game_master = Mock()
    consumer.channel_layer = RecordingChannelLayer()
    consumer.room_group_name = "game_bot-room"

    with patch(
        "chat.consumers_modules.game_consumer.asyncio.sleep",
        new=AsyncMock(),
    ) as sleep:
        await consumer.receive(
            json.dumps({"command": {"action": "inspect"}})
        )

    payloads = [
        event["payload"]
        for event in consumer.channel_layer.events
        if event["event"] == "action_result"
    ]
    assert payloads[0]["actor"] == {
        "participant_id": 8,
        "name": "Hero",
        "is_ai": False,
    }
    assert payloads[0]["turn_state"]["current_player_id"] == 7
    assert payloads[1]["actor"] == {
        "participant_id": 7,
        "name": "Demo Companion",
        "is_ai": True,
    }
    assert payloads[1]["turn_state"]["current_player_id"] == 8
    sleep.assert_awaited_once_with(3)


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
