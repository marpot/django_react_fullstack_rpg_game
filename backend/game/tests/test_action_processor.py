import pytest
from django.contrib.auth import get_user_model

from game.core.action_processor import ActionProcessor

from game.state.game_state_manager import GameStateManager
from game.state.runtime.models import Player, Enemy

from game.services.combat_service import CombatService
from game.services.dice_service import DiceService


from accounts.models import PlayerCharacter

from world.models import Adventure, Enemy as EnemyORM


pytestmark = pytest.mark.django_db


def test_attack_action():
    state = GameStateManager()
    state.get_or_create_room("testroom")

    # =========================
    # runtime player
    # =========================
    state.add_player(
        "testroom",
        1,
        Player(
            id=1,
            name="Hero",
            hp=100,
            max_hp=100,
            attack_bonus=10,
            damage_die=8,
            damage_bonus=2,
            defense=5,
        )
    )

    # =========================
    # runtime enemy
    # =========================
    state.add_enemy(
        "testroom",
        Enemy(
            id="goblin",
            name="goblin",
            hp=10,
            defense=2,
            attack_bonus=1,
            damage_die=6,
            damage_bonus=1,
        )
    )

    # =========================
    # ORM setup
    # =========================
    User = get_user_model()
    user = User.objects.create_user(username="hero", password="x")

    PlayerCharacter.objects.create(
        id=1,
        user=user,
        name="Hero",
        health=100,
        max_health=100,
    )

    adventure = Adventure.objects.create(
        title="test",
        creator=user  # WAŻNE jeśli masz FK required
    )

    EnemyORM.objects.create(
        id=1,
        name="goblin",
        hp=10,
        defense=2,
        attack_bonus=1,
        damage_die=6,
        damage_bonus=1,
        adventure=adventure,  # KLUCZOWE FIX
    )

    # =========================
    # ACTION
    # =========================
    dice = DiceService(seed=1)
    combat = CombatService(dice)


    processor = ActionProcessor(state_manager=state, combat_service=combat)

    parsed = {
        "action": "attack",
        "target": "goblin",
        "room": "testroom",
        "user_id": 1
    }

    result = processor.process(parsed)

    # =========================
    # ASSERTS
    # =========================
    assert "action" in result
    assert result["action"] == "attack"
    assert state.get_room("testroom").enemies["goblin"].hp <= 10