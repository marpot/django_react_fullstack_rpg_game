import pytest
from django.contrib.auth import get_user_model

from game.core.action_processor import ActionProcessor

from game.state.game_state_manager import GameStateManager
from game.state.runtime.models import Player, Enemy

from game.services.combat_service import CombatService
from game.services.dice_service import DiceService


from accounts.models import PlayerCharacter
from chat.models import Room
from chat.services.room_participants_service import RoomParticipantsService

from world.models import Adventure, Enemy as EnemyORM


pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("fake_llm_provider")]


def test_attack_action():
    state = GameStateManager()

    User = get_user_model()
    user = User.objects.create_user(username="hero", password="x")

    character = PlayerCharacter.objects.create(
        user=user,
        name="Hero",
        health=100,
        max_health=100,
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

    EnemyORM.objects.create(
        name="goblin",
        hp=10,
        defense=2,
        attack_bonus=1,
        damage_die=6,
        damage_bonus=1,
        adventure=adventure,
    )

    room.turn_order = [participant.id]
    room.current_player_id = participant.id
    room.player_histories = {participant.id: []}

    dice = DiceService(seed=1)
    combat = CombatService(dice)

    processor = ActionProcessor(state_manager=state, combat_service=combat)

    result = processor.process({
        "action": "attack",
        "target": "goblin",
        "room": room_record.id,
        "participant_id": participant.id,
        'adventure': adventure.id
    })

    assert result["action"] == "attack"
    assert "error" not in result
    assert state.get_room(room_record.id).enemies["goblin"].hp < 10


def test_turn_progresses_and_tracks_player_history():
    state = GameStateManager()

    User = get_user_model()
    user_one = User.objects.create_user(username="hero1", password="x")
    user_two = User.objects.create_user(username="hero2", password="x")

    character_one = PlayerCharacter.objects.create(user=user_one, name="Hero1")
    character_two = PlayerCharacter.objects.create(user=user_two, name="Hero2")
    adventure = Adventure.objects.create(title="turn-test", creator=user_one)
    room_record = Room.objects.create(
        name="turnroom",
        owner=user_one,
        adventure=adventure,
    )
    participant_one = RoomParticipantsService.add_human(
        room_record,
        user_one,
        character_one,
    )
    participant_two = RoomParticipantsService.add_human(
        room_record,
        user_two,
        character_two,
    )
    room = state.get_or_create_room(room_record.id)

    room.players[participant_one.id] = Player(
        id=participant_one.id,
        name="Hero1",
        hp=100,
        max_hp=100,
        attack_bonus=10,
        damage_die=8,
        damage_bonus=2,
        defense=5,
    )
    room.players[participant_two.id] = Player(
        id=participant_two.id,
        name="Hero2",
        hp=100,
        max_hp=100,
        attack_bonus=10,
        damage_die=8,
        damage_bonus=2,
        defense=5,
    )

    room.turn_order = [participant_one.id, participant_two.id]
    room.current_player_id = participant_one.id
    room.current_turn_index = 0
    room.player_histories = {participant_one.id: [], participant_two.id: []}

    processor = ActionProcessor(state_manager=state)

    result = processor.process({
        "action": "inspect",
        "room": room_record.id,
        "participant_id": participant_one.id,
        "adventure": adventure.id,
        "world": {},
    })

    assert result["action"] == "inspect"
    assert room.current_player_id == participant_two.id
    assert room.player_histories[participant_one.id][-1]["action"] == "inspect"


@pytest.mark.parametrize("action", ["attack", "move"])
def test_narration_provider_failure_preserves_action_and_turn(action, fake_llm_provider):
    state = GameStateManager()
    room = state.get_or_create_room("narration-failure")
    room.players[1] = Player(
        id=1, name="Hero", hp=100, max_hp=100, attack_bonus=20,
        damage_die=8, damage_bonus=2, defense=10,
    )
    room.players[2] = Player(
        id=2, name="Next", hp=100, max_hp=100, attack_bonus=1,
        damage_die=6, damage_bonus=0, defense=10,
    )
    room.enemies["goblin"] = Enemy(
        id="goblin", name="goblin", hp=30, defense=0,
        attack_bonus=0, damage_die=6, damage_bonus=0,
    )
    room.turn_order = [1, 2]
    room.current_player_id = 1
    room.player_histories = {1: [], 2: []}
    fake_llm_provider.error = RuntimeError("provider unavailable")

    processor = ActionProcessor(
        state_manager=state,
        combat_service=CombatService(DiceService(seed=1)),
    )
    result = processor.process({
        "action": action,
        "target": "goblin" if action == "attack" else "north",
        "room": room.name,
        "participant_id": 1,
    })

    assert result["action"] == result["event_type"] == action
    assert result["text"] == f"Zdarzenie ({action}) się rozwija."
    assert "error" not in result["result"]
    assert room.player_histories[1][-1]["action"] == action
    assert result["turn_state"]["current_player_id"] == room.current_player_id == 2
    if action == "attack":
        assert room.enemies["goblin"].hp < 30
        assert result["result"]["attacker_damage"] > 0
    else:
        assert room.players[1].location == result["result"]["location"] == "north"
