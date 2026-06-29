import pytest
from django.contrib.auth import get_user_model

from game.core.action_processor import ActionProcessor
from game.state.game_state_manager import GameStateManager
from game.state.runtime.models import Player, Enemy as RuntimeEnemy

from accounts.models import PlayerCharacter
from world.models import Adventure, Enemy as EnemyORM

pytestmark = pytest.mark.django_db


def _base_env():
    state = GameStateManager()
    processor = ActionProcessor(state)

    User = get_user_model()
    user = User.objects.create_user(username="hero", password="x")

    PlayerCharacter.objects.create(
        user=user,
        name="Hero",
        health=100,
        max_health=100
    )

    adventure = Adventure.objects.create(
        title="test",
        creator=user
    )

    return state, processor, user, adventure


# -----------------------------
# CONTRACT TEST 1: SHAPE CHECK
# -----------------------------
def test_attack_response_contract_shape():
    state, processor, user, adventure = _base_env()

    state.add_player(
        "testroom",
        user.id,
        Player(
            id=user.id,
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
        "testroom",
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
        "room": "testroom",
        "user_id": user.id,
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
    state, processor, user, adventure = _base_env()

    state.add_player(
        "testroom",
        user.id,
        Player(
            id=user.id,
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
        "testroom",
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
        "room": "testroom",
        "user_id": user.id,
        "adventure": adventure.id
    })

    assert "error" not in result
    assert state.get_room("testroom").enemies["goblin"].hp < 30


# -----------------------------
# CONTRACT TEST 3: NO NEGATIVE HP
# -----------------------------
def test_enemy_hp_never_negative():
    state, processor, user, adventure = _base_env()

    state.add_player(
        "testroom",
        user.id,
        Player(
            id=user.id,
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
        "testroom",
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
        "room": "testroom",
        "user_id": user.id,
        "adventure": adventure.id
    })

    assert "error" not in result
    assert state.get_room("testroom").enemies["goblin"].hp >= 0