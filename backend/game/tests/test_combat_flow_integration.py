from unittest.mock import Mock

from game.state.game_state_manager import GameStateManager
from game.core.action_processor import ActionProcessor
from game.core.game_command import GameCommand
from game.services.game_start_service import GameStartService
from game.state.runtime.models import Enemy as RuntimeEnemy
from accounts.models import PlayerCharacter
from chat.models import Room
from chat.services.room_participants_service import RoomParticipantsService
from django.contrib.auth import get_user_model
from game_instances.services.llm.orchestrator.llm_service import LLMService
from world.models import Adventure, Enemy as EnemyORM
from world.seeders.world_seeder import WorldSeeder
import pytest

pytestmark = pytest.mark.django_db


def _combat_room():
    user = get_user_model().objects.create_user(username="hero", password="x")
    character = PlayerCharacter.objects.create(
        user=user, name="Hero", health=100, max_health=100
    )
    adventure = Adventure.objects.create(
        title="test", description="Combat test", creator=user
    )
    room = Room.objects.create(name="testroom", owner=user, adventure=adventure)
    participant = RoomParticipantsService.add_human(room, user, character)
    EnemyORM.objects.create(
        name="goblin", hp=30, defense=2, attack_bonus=1,
        damage_die=6, damage_bonus=1, adventure=adventure,
    )
    return room, participant, adventure


def _start_game(state, room, adventure):
    return GameStartService(
        seeder=WorldSeeder(state),
        llm=LLMService(),
        notifier=Mock(),
        state_manager=state,
    ).start_game(adventure.id, room.id, adventure=adventure)


def test_full_combat_flow(fake_llm_provider):
    state = GameStateManager()
    room, participant, adventure = _combat_room()
    world = _start_game(state, room, adventure)
    runtime = state.get_room(room.id)

    result = ActionProcessor(state).process(
        GameCommand(action="attack", target="goblin"),
        room=room.id,
        participant_id=participant.id,
        adventure=adventure.id,
        world=world,
    )

    assert result["action"] == "attack"
    assert result["result"]["attacker_damage"] > 0
    assert runtime.enemies["goblin"].hp < 30
    assert runtime.player_histories[participant.id][0]["action"] == "attack"
    assert runtime.current_player_id == participant.id

def test_game_start_seeds_enemies_before_attack(fake_llm_provider):
    state = GameStateManager()
    room, participant, adventure = _combat_room()
    runtime = state.get_or_create_room(room.id)
    runtime.enemies = {}
    processor = ActionProcessor(state)
    command = GameCommand(action="attack", target="goblin")

    rejected = processor.process(
        command, room=room.id, participant_id=participant.id,
        adventure=adventure.id,
    )
    assert rejected["result"]["error"] == "participant_not_in_game"
    assert runtime.enemies == {}

    world = _start_game(state, room, adventure)
    assert runtime.started is True
    assert list(runtime.enemies) == ["goblin"]
    assert runtime.enemies["goblin"].hp == 30

    result = processor.process(
        command, room=room.id, participant_id=participant.id,
        adventure=adventure.id, world=world,
    )
    assert result["action"] == "attack"
    assert result["result"]["attacker_damage"] > 0
    assert runtime.enemies["goblin"].hp < 30

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
        "participant_id": user.id,
        "adventure": adventure.id
    })

    assert "error" not in result
    assert room.enemies["goblin"].hp >= 0
