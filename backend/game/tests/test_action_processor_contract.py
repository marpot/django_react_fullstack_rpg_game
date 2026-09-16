import pytest
from django.contrib.auth import get_user_model

from game.core.action_processor import ActionProcessor
from game.state.game_state_manager import GameStateManager
from game.state.runtime.models import Player, Enemy as RuntimeEnemy

from accounts.models import PlayerCharacter
from chat.models import Room
from chat.services.room_participants_service import RoomParticipantsService
from world.models import Adventure, Enemy as EnemyORM

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("fake_llm_provider")]


def _base_env():
    state = GameStateManager()
    processor = ActionProcessor(state)

    User = get_user_model()
    user = User.objects.create_user(username="hero", password="x")

    character = PlayerCharacter.objects.create(
        user=user,
        name="Hero",
        health=100,
        max_health=100
    )

    adventure = Adventure.objects.create(
        title="test",
        creator=user
    )
    room_record = Room.objects.create(
        name="testroom",
        owner=user,
        adventure=adventure,
    )
    participant = RoomParticipantsService.add_human(
        room_record,
        user,
        character,
    )
    room = state.get_or_create_room(room_record.id)
    room.turn_order = [participant.id]
    room.current_player_id = participant.id
    room.player_histories = {participant.id: []}

    return state, processor, participant, adventure, room_record


# -----------------------------
# CONTRACT TEST 1: SHAPE CHECK
# -----------------------------
def test_attack_response_contract_shape():
    state, processor, participant, adventure, room_record = _base_env()

    state.add_player(
        room_record.id,
        participant.id,
        Player(
            id=participant.id,
            name="Hero",
            hp=100,
            max_hp=100,
            attack_bonus=10,
            damage_die=8,
            damage_bonus=2,
            defense=5,
        )
    )

    state.add_enemy(
        room_record.id,
        RuntimeEnemy(
            id="goblin",
            name="goblin",
            hp=10,
            defense=2,
            attack_bonus=1,
            damage_die=6,
            damage_bonus=1,
        )
    )

    EnemyORM.objects.create(
        name="goblin",
        hp=10,
        defense=2,
        attack_bonus=1,
        damage_die=6,
        damage_bonus=1,
        adventure=adventure,
    )

    result = processor.process({
        "action": "attack",
        "target": "goblin",
        "room": room_record.id,
        "participant_id": participant.id,
        "adventure": adventure.id
    })

    assert isinstance(result, dict)
    assert "event_type" in result
    assert "text" in result
    assert isinstance(result["result"], dict)
    assert isinstance(result["world"], dict)
    assert isinstance(result["choices"], list)


# -----------------------------
# CONTRACT TEST 2: ATTACK CHANGES STATE
# -----------------------------
def test_attack_reduces_hp():
    state, processor, participant, adventure, room_record = _base_env()

    state.add_player(
        room_record.id,
        participant.id,
        Player(
            id=participant.id,
            name="Hero",
            hp=100,
            max_hp=100,
            attack_bonus=10,
            damage_die=8,
            damage_bonus=2,
            defense=5,
        )
    )

    state.add_enemy(
        room_record.id,
        RuntimeEnemy(
            id="goblin",
            name="goblin",
            hp=30,
            defense=2,
            attack_bonus=1,
            damage_die=6,
            damage_bonus=1,
        )
    )

    EnemyORM.objects.create(
        name="goblin",
        hp=30,
        defense=2,
        attack_bonus=1,
        damage_die=6,
        damage_bonus=1,
        adventure=adventure,
    )

    result = processor.process({
        "action": "attack",
        "target": "goblin",
        "room": room_record.id,
        "participant_id": participant.id,
        "adventure": adventure.id
    })

    assert "error" not in result
    assert state.get_room(room_record.id).enemies["goblin"].hp < 30


# -----------------------------
# CONTRACT TEST 3: NO NEGATIVE HP
# -----------------------------
def test_enemy_hp_never_negative():
    state, processor, participant, adventure, room_record = _base_env()

    state.add_player(
        room_record.id,
        participant.id,
        Player(
            id=participant.id,
            name="Hero",
            hp=100,
            max_hp=100,
            attack_bonus=10,
            damage_die=8,
            damage_bonus=2,
            defense=5,
        )
    )

    state.add_enemy(
        room_record.id,
        RuntimeEnemy(
            id="goblin",
            name="goblin",
            hp=5,
            defense=0,
            attack_bonus=0,
            damage_die=6,
            damage_bonus=0,
        )
    )

    EnemyORM.objects.create(
        name="goblin",
        hp=5,
        defense=0,
        attack_bonus=0,
        damage_die=6,
        damage_bonus=0,
        adventure=adventure,
    )

    result = processor.process({
        "action": "attack",
        "target": "goblin",
        "room": room_record.id,
        "participant_id": participant.id,
        "adventure": adventure.id
    })

    assert "error" not in result
    assert state.get_room(room_record.id).enemies["goblin"].hp >= 0
