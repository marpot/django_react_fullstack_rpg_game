from game.state.game_state_manager import GameStateManager
from game.core.action_processor import ActionProcessor
from game.state.runtime.models import Player, Enemy as RuntimeEnemy
from accounts.models import PlayerCharacter
from django.contrib.auth import get_user_model
from world.models import Adventure, Enemy as EnemyORM
import pytest

pytestmark = pytest.mark.django_db


def test_full_combat_flow():
    state = GameStateManager()
    processor = ActionProcessor(state)

    room = state.get_or_create_room("testroom")

    # =========================
    # Django user
    # =========================
    User = get_user_model()
    user = User.objects.create_user(username="hero", password="x")

    # =========================
    # ORM player (required by system)
    # =========================
    PlayerCharacter.objects.create(
        user=user,
        name="Hero",
        health=100,
        max_health=100
    )

    # =========================
    # Adventure (REQUIRED by FK)
    # =========================
    adventure = Adventure.objects.create(
        title="test",
        creator=user
    )

    # =========================
    # Runtime player (combat layer)
    # =========================
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
            defense=5
        )
    )

    # =========================
    # ORM enemy
    # =========================
    EnemyORM.objects.create(
        name="goblin",
        hp=30,
        defense=2,
        attack_bonus=1,
        damage_die=6,
        damage_bonus=1,
        adventure=adventure
    )

    # =========================
    # Runtime enemy
    # =========================
    room.enemies["goblin"] = RuntimeEnemy(
        id="goblin",
        name="goblin",
        hp=30,
        defense=2,
        attack_bonus=1,
        damage_die=6,
        damage_bonus=1
    )

    # =========================
    # ACT
    # =========================
    result = processor.process({
        "action": "attack",
        "target": "goblin",
        "room": "testroom",
        "user_id": user.id,
        "adventure": adventure.id
    })

    # =========================
    # ASSERT
    # =========================
    assert "error" not in result
    assert result["action"] == "attack"
    assert result["result"] is not None
    assert room.enemies["goblin"].hp < 30

def test_attack_triggers_enemy_seed_when_room_is_empty():
    state = GameStateManager()
    processor = ActionProcessor(state)

    room = state.get_or_create_room("testroom")
    room.enemies = {}

    User = get_user_model()
    user = User.objects.create_user(
        username="hero",
        password="x"
    )

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

    EnemyORM.objects.create(
        name="goblin",
        hp=30,
        defense=2,
        attack_bonus=1,
        damage_die=6,
        damage_bonus=1,
        adventure=adventure
    )

    result = processor.process({
        "action": "attack",
        "target": "goblin",
        "room": "testroom",
        "user_id": user.id,
        "adventure": adventure.id
    })

    assert "error" not in result
    assert "goblin" in room.enemies
    assert len(room.enemies) == 1
    assert room.enemies["goblin"].hp <= 30

def test_enemy_hp_never_goes_negative():
    state = GameStateManager()
    processor = ActionProcessor(state)

    room = state.get_or_create_room("testroom")

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
    
    EnemyORM.objects.create(
        name="goblin",
        hp=5,
        defense=0,
        attack_bonus=0,
        damage_die=6,
        damage_bonus=0,
        adventure=adventure
    )

    # runtime enemy (bez seeda, kontrola testu)
    room.enemies["goblin"] = RuntimeEnemy(
        id="goblin",
        name="goblin",
        hp=5,
        defense=0,
        attack_bonus=0,
        damage_die=6,
        damage_bonus=0
    )

    

    result = processor.process({
        "action": "attack",
        "target": "goblin",
        "room": "testroom",
        "user_id": user.id,
        "adventure": adventure.id
    })

    assert "error" not in result
    assert room.enemies["goblin"].hp >= 0