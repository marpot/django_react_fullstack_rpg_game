import pytest

from game.core.action_processor import ActionProcessor
from game.core.game_command import GameCommand
from game.services.combat_service import CombatService
from game.services.dice_service import DiceService
from game.state.game_state_manager import GameStateManager
from game.state.runtime.models import Enemy, Player


pytestmark = pytest.mark.usefixtures("fake_llm_provider")


def _player(participant_id):
    return Player(
        id=participant_id, name=f"Player {participant_id}", hp=100, max_hp=100,
        attack_bonus=20, damage_die=8, damage_bonus=2, defense=10,
    )


def _processor():
    state = GameStateManager()
    room = state.get_or_create_room("command-room")
    room.players = {1: _player(1), 2: _player(2)}
    room.enemies["goblin"] = Enemy(
        id="goblin", name="goblin", hp=30, defense=0,
        attack_bonus=0, damage_die=6, damage_bonus=0,
    )
    room.turn_order = [1, 2]
    room.current_player_id = 1
    room.player_histories = {1: [], 2: []}
    processor = ActionProcessor(state, combat_service=CombatService(DiceService(seed=1)))
    return processor, room


def test_valid_attack_command():
    command = GameCommand.from_mapping({"action": "attack", "target": "goblin"})

    assert command == GameCommand(action="attack", target="goblin")


def test_valid_move_command_reaches_action_processor():
    processor, room = _processor()

    result = processor.process(
        GameCommand(action="move", target="north"),
        room=room.name,
        participant_id=1,
    )

    assert result["action"] == "move"
    assert room.players[1].location == "north"
    assert room.player_histories[1][-1]["action"] == "move"


def test_unknown_action_is_rejected_before_mechanics():
    processor, room = _processor()

    with pytest.raises(ValueError, match="invalid_action"):
        GameCommand(action="teleport")
    result = processor.process({"action": "teleport", "room": room.name, "participant_id": 1})

    assert result["result"]["error"] == "invalid_action"
    assert room.current_player_id == 1
    assert room.player_histories == {1: [], 2: []}


def test_client_result_fields_cannot_control_attack_or_identity():
    processor, room = _processor()
    untrusted = {
        "action": "attack", "target": "goblin", "hp": 999, "damage": 999,
        "result": {"winner": "player"}, "participant_id": 2, "room": "other-room",
    }
    command = GameCommand.from_mapping(untrusted)

    assert command == GameCommand(action="attack", target="goblin")
    assert not hasattr(command, "participant_id")
    result = processor.process(untrusted, room=room.name, participant_id=1)

    assert result["action"] == "attack"
    assert room.enemies["goblin"].hp == 30 - result["result"]["attacker_damage"]
    assert room.players[1].hp == 100 - result["result"]["defender_damage"]
    assert room.players[2].hp == 100
    assert room.player_histories[1][-1]["action"] == "attack"
    assert room.player_histories[2] == []
    assert room.current_player_id == 2


def test_explicit_missing_identity_does_not_fall_back_to_command():
    processor, room = _processor()

    result = processor.process(
        {"action": "inspect", "participant_id": 1},
        room=room.name,
        participant_id=None,
    )

    assert result["result"]["error"] == "missing_participant_id"
    assert room.player_histories == {1: [], 2: []}
