import pytest
from unittest.mock import patch

from game.core.action_processor import ActionProcessor
from game.core.game_command import GameCommand
from game.npc.npc_models import NPC
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


def _processor(narrate_fn=None):
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
    processor = ActionProcessor(
        state, combat_service=CombatService(DiceService(seed=1)), narrate_fn=narrate_fn,
    )
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


def test_processor_does_not_construct_ai_services():
    with (
        patch("game_instances.services.llm.orchestrator.llm_service.LLMService", side_effect=AssertionError),
        patch("game_instances.services.llm.core.llm_client.LLMClient", side_effect=AssertionError),
    ):
        processor, room = _processor()
        result = processor.process(GameCommand(action="inspect"), room=room.name, participant_id=1)

    assert result["action"] == "inspect"
    assert room.current_player_id == 2


def test_narration_receives_resolved_result_and_cannot_change_mechanics():
    observed = {}

    def narrate(action, canonical_result, world, details):
        observed["action"] = action
        observed["result"] = canonical_result.copy()
        observed["hp_at_narration"] = room.enemies["goblin"].hp
        observed["details"] = details
        canonical_result["attacker_damage"] = 999
        return {"text": "Goblin ginie! Zadajesz 999 obrażeń."}

    processor, room = _processor(narrate_fn=narrate)
    result = processor.process(
        GameCommand(action="attack", target="goblin"), room=room.name, participant_id=1,
    )

    assert observed["action"] == "attack"
    assert observed["result"] == result["result"]
    assert observed["hp_at_narration"] == room.enemies["goblin"].hp
    assert observed["details"]["actor"] == "Player 1"
    assert observed["details"]["target"] == "goblin"
    assert room.enemies["goblin"].hp == 30 - result["result"]["attacker_damage"]
    assert room.players[1].hp == 100 - result["result"]["defender_damage"]
    assert room.player_histories[1][-1]["result"] == result["result"]
    assert room.current_player_id == 2


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


def test_talk_uses_existing_npc_dialogue_without_changing_game_state():
    processor, room = _processor()
    room.npcs["guide"] = NPC(id="guide", name="Guide", dialog=["Witaj, wędrowcze."])
    hp_before = {player_id: player.hp for player_id, player in room.players.items()}
    enemy_hp_before = room.enemies["goblin"].hp

    result = processor.process(
        GameCommand(action="talk", target="guide"),
        room=room.name,
        participant_id=1,
    )

    assert result["action"] == "talk"
    assert result["text"] == "Witaj, wędrowcze."
    assert result["result"]["npc"] == "Guide"
    assert {player_id: player.hp for player_id, player in room.players.items()} == hp_before
    assert room.enemies["goblin"].hp == enemy_hp_before
    assert room.current_player_id == 1
    assert room.current_turn_index == 0
    assert room.player_histories == {1: [], 2: []}


@pytest.mark.parametrize("target", ["unknown", None])
def test_talk_with_missing_npc_returns_controlled_error(target):
    processor, room = _processor()

    result = processor.process(
        GameCommand(action="talk", target=target),
        room=room.name,
        participant_id=1,
    )

    assert result["action"] == "talk"
    assert result["result"]["error"] == "npc_not_found"
    assert room.current_player_id == 1
    assert room.player_histories == {1: [], 2: []}
