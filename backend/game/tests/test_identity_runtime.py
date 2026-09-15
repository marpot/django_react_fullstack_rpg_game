import pytest
from django.contrib.auth import get_user_model
from unittest.mock import Mock

from accounts.models import PlayerCharacter
from chat.models import Room, RoomParticipant
from chat.services.room_participants_service import RoomParticipantsService
from game.core.action_processor import ActionProcessor
from game.services.game_start_service import GameStartService
from game.services.game_turn_service import GameTurnService
from game.state.game_state_manager import GameStateManager
from game.state.runtime.runtime_player_service import RuntimePlayerService
from game.state.runtime.models import Player


pytestmark = pytest.mark.django_db


@pytest.fixture
def room_and_user():
    user_model = get_user_model()
    user = user_model.objects.create_user(username="hero", password="x")
    room = Room.objects.create(name="identity-room", owner=user)
    return room, user


def test_runtime_player_uses_participant_identity(room_and_user):
    room, user = room_and_user
    character = PlayerCharacter.objects.create(
        user=user,
        name="Hero",
        health=72,
        max_health=100,
        strength=14,
    )
    participant = RoomParticipantsService.add_human(room, user, character)
    state = GameStateManager()
    room_state = state.get_or_create_room(room.id)

    runtime_player = RuntimePlayerService(state).get_or_create(
        room_state,
        participant.id,
    )

    assert runtime_player.id == participant.id
    assert runtime_player.user_id == user.id
    assert runtime_player.character_id == character.id
    assert runtime_player.hp == character.health
    assert runtime_player.max_hp == character.max_health
    assert runtime_player.attack_bonus == character.strength
    assert room_state.players == {participant.id: runtime_player}


def test_ai_runtime_player_has_no_user_or_character(room_and_user):
    room, _ = room_and_user
    participant = RoomParticipantsService.add_ai(room, "Goblin guide")
    state = GameStateManager()
    room_state = state.get_or_create_room(room.id)

    runtime_player = RuntimePlayerService(state).get_or_create(
        room_state,
        participant.id,
    )

    assert runtime_player.id == participant.id
    assert runtime_player.user_id is None
    assert runtime_player.character_id is None


def test_runtime_player_rejects_character_owned_by_another_user(room_and_user):
    room, user = room_and_user
    other_user = get_user_model().objects.create_user(
        username="other-runtime-hero",
        password="x",
    )
    character = PlayerCharacter.objects.create(user=other_user, name="Other")
    participant = RoomParticipant.objects.create(
        room=room,
        user=user,
        character=character,
        name="Invalid",
        is_ai=False,
    )
    state = GameStateManager()
    room_state = state.get_or_create_room(room.id)

    runtime_player = RuntimePlayerService(state).get_or_create(
        room_state,
        participant.id,
    )

    assert runtime_player is None
    assert participant.id not in room_state.players


def test_add_human_rejects_character_owned_by_another_user(room_and_user):
    room, user = room_and_user
    other_user = get_user_model().objects.create_user(
        username="other-hero",
        password="x",
    )
    character = PlayerCharacter.objects.create(user=other_user, name="Other")

    with pytest.raises(ValueError, match="does not belong"):
        RoomParticipantsService.add_human(room, user, character)


def test_add_human_requires_character(room_and_user):
    room, user = room_and_user

    with pytest.raises(ValueError, match="requires a PlayerCharacter"):
        RoomParticipantsService.add_human(room, user, None)


def test_turn_state_uses_participant_ids():
    state = GameStateManager()
    room = state.get_or_create_room("turn-room")
    turn_service = GameTurnService(state)

    turn_service.register_player(room, 41)
    turn_service.register_player(room, 99)

    assert room.turn_order == [41, 99]
    assert room.current_player_id == 41
    assert room.player_histories == {41: [], 99: []}
    assert turn_service.build_state(room, 41)["is_your_turn"] is True
    assert turn_service.build_state(room, 99)["is_your_turn"] is False


def test_game_start_initializes_runtime_turns_from_participants(room_and_user):
    room, user = room_and_user
    character = PlayerCharacter.objects.create(user=user, name="Hero")
    human = RoomParticipantsService.add_human(room, user, character)
    ai = RoomParticipantsService.add_ai(room, "Guide")
    state = GameStateManager()
    llm = Mock()
    llm.generate_world.return_value = {}
    llm.generate_intro.return_value = {}

    GameStartService(
        seeder=Mock(),
        llm=llm,
        notifier=Mock(),
        state_manager=state,
    ).start_game(adventure_id=123, room_id=room.id)

    room_state = state.get_room(room.id)
    assert room_state.players.keys() == {human.id, ai.id}
    assert room_state.turn_order == [human.id, ai.id]
    assert room_state.current_player_id == human.id
    assert room_state.player_histories == {human.id: [], ai.id: []}


def test_action_processor_rejects_action_outside_current_participant_turn():
    state = GameStateManager()
    room = state.get_or_create_room("blocked-turn-room")
    room.players[41] = Player(
        id=41,
        name="First",
        hp=100,
        max_hp=100,
        attack_bonus=5,
        damage_die=6,
        damage_bonus=1,
        defense=10,
    )
    room.players[99] = Player(
        id=99,
        name="Second",
        hp=100,
        max_hp=100,
        attack_bonus=5,
        damage_die=6,
        damage_bonus=1,
        defense=10,
    )
    room.turn_order = [41, 99]
    room.current_player_id = 41

    result = ActionProcessor(state).process({
        "action": "inspect",
        "room": "blocked-turn-room",
        "participant_id": 99,
        "world": {},
    })

    assert result["action"] == "error"
    assert result["result"]["error"] == "not_your_turn"
    assert room.current_player_id == 41


def test_action_processor_rejects_participant_outside_active_game():
    state = GameStateManager()
    room = state.get_or_create_room("membership-room")
    room.players[41] = Player(
        id=41,
        name="First",
        hp=100,
        max_hp=100,
        attack_bonus=5,
        damage_die=6,
        damage_bonus=1,
        defense=10,
    )
    room.turn_order = [41]
    room.current_player_id = 41
    room.player_histories = {41: []}

    result = ActionProcessor(state).process({
        "action": "inspect",
        "room": "membership-room",
        "participant_id": 99,
        "world": {},
    })

    assert result["action"] == "error"
    assert result["result"]["error"] == "participant_not_in_game"
    assert room.turn_order == [41]
    assert room.current_player_id == 41
    assert room.player_histories == {41: []}
