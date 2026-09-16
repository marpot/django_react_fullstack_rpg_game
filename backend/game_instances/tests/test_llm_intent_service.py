import json

import pytest

from game.core.action_processor import ActionProcessor
from game.core.game_command import ALLOWED_ACTIONS, GameCommand
from game.npc.npc_models import NPC
from game.state.game_state_manager import GameStateManager
from game.state.runtime.models import Enemy, Player
from game_instances.services.llm.core.llm_client import LLMClient
from game_instances.services.llm.intent.game_context import GameContextBuilder
from game_instances.services.llm.orchestrator.llm_service import LLMService


NATURAL_INPUT = "Spróbuję zdzielić goblina mieczem zanim podejdzie bliżej."


class FakeProvider:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def complete(self, system_prompt, user_prompt):
        self.calls.append((system_prompt, user_prompt))
        if self.error is not None:
            raise self.error
        return self.response


@pytest.fixture(autouse=True)
def isolate_default_provider(monkeypatch):
    monkeypatch.setattr(
        "game_instances.services.llm.core.llm_client.GroqProvider",
        lambda: FakeProvider(response="Narracja testowa."),
    )


def _runtime():
    state = GameStateManager()
    room = state.get_or_create_room("llm-intent-room")
    room.players[1] = Player(
        id=1, name="Hero", hp=80, max_hp=100, attack_bonus=10,
        damage_die=6, damage_bonus=0, defense=10, location="crypt",
    )
    room.players[2] = Player(
        id=2, name="Other", hp=100, max_hp=100, attack_bonus=10,
        damage_die=6, damage_bonus=0, defense=10,
    )
    room.enemies["goblin"] = Enemy(
        id="goblin", name="goblin", hp=12, defense=5,
        attack_bonus=1, damage_die=6, damage_bonus=0,
    )
    room.npcs["guide"] = NPC(id="guide", name="Guide")
    room.turn_order = [1, 2]
    room.current_player_id = 1
    room.player_histories = {
        1: [{"action": "inspect", "result": {"damage": 999}}],
        2: [],
    }
    return state, room


@pytest.mark.parametrize("message", ["attack goblin", "inspect room", "move north"])
def test_deterministic_commands_do_not_call_provider(message):
    state, room = _runtime()
    provider = FakeProvider(error=AssertionError("provider must not run"))
    service = LLMService(intent_client=LLMClient(provider))

    parsed = service.parse_player_input(
        message, state_manager=state, room=room.name, participant_id=1,
    )

    assert GameCommand.from_mapping(parsed).action in ALLOWED_ACTIONS
    assert provider.calls == []


def test_natural_text_uses_bounded_server_context_and_returns_command():
    state, room = _runtime()
    provider = FakeProvider('{"action":"attack","target":"goblin","method":"sword"}')
    service = LLMService(intent_client=LLMClient(provider))

    parsed = service.parse_player_input(
        {"input": NATURAL_INPUT, "world": {"hp": 999}, "memory": {"damage": 999}},
        state_manager=state, room=room.name, participant_id=1,
    )

    assert GameCommand.from_mapping(parsed) == GameCommand(
        action="attack", target="goblin", method="sword",
    )
    assert len(provider.calls) == 1
    prompt = json.loads(provider.calls[0][1])
    assert set(prompt) == {"message", "game_context"}
    assert prompt["message"] == NATURAL_INPUT
    assert prompt["game_context"] == {
        "current_player": "Hero",
        "current_location": "crypt",
        "enemies": ["goblin"],
        "npcs": ["Guide"],
        "allowed_actions": sorted(ALLOWED_ACTIONS),
        "recent_actions": ["inspect"],
    }
    assert "hp" not in provider.calls[0][1]
    assert "damage" not in provider.calls[0][1]
    assert "participant_id" not in provider.calls[0][1]


def test_game_context_limits_names_and_history():
    state, room = _runtime()
    room.players[1].name = "H" * 100
    room.players[1].location = "L" * 100
    room.player_histories[1] = [{"action": "inspect", "result": {"hp": 999}}] * 10
    for index in range(20):
        room.enemies[str(index)] = Enemy(
            id=str(index), name=f"enemy-{index}-" + "x" * 100,
            hp=10, defense=0, attack_bonus=0, damage_die=6, damage_bonus=0,
        )

    context = GameContextBuilder().build(state, room.name, 1)

    json.dumps(context)
    assert len(context["current_player"]) == 80
    assert len(context["current_location"]) == 80
    assert len(context["enemies"]) == 12
    assert all(len(name) <= 80 for name in context["enemies"])
    assert context["recent_actions"] == ["inspect"] * 3


@pytest.mark.parametrize("response", [
    "not JSON",
    '{"action":"teleport","target":"crypt","method":null}',
    '{"action":null,"target":null,"method":null}',
    '{"action":"attack","target":"goblin","method":"sword",'
    '"hp":999,"damage":999,"participant_id":2}',
])
def test_invalid_provider_intent_is_rejected_without_mechanics(response):
    state, room = _runtime()
    service = LLMService(intent_client=LLMClient(FakeProvider(response=response)))

    parsed = service.parse_player_input(
        NATURAL_INPUT, state_manager=state, room=room.name, participant_id=1,
    )
    result = ActionProcessor(state).process(parsed, room=room.name, participant_id=1)

    assert result["result"]["error"] == "invalid_action"
    assert room.players[1].hp == 80
    assert room.players[1].location == "crypt"
    assert room.enemies["goblin"].hp == 12
    assert room.player_histories[1] == [{"action": "inspect", "result": {"damage": 999}}]
    assert room.current_player_id == 1


def test_provider_exception_does_not_change_state_or_turn():
    state, room = _runtime()
    service = LLMService(intent_client=LLMClient(FakeProvider(
        error=RuntimeError("provider unavailable")
    )))

    parsed = service.parse_player_input(
        NATURAL_INPUT, state_manager=state, room=room.name, participant_id=1,
    )
    result = ActionProcessor(state).process(parsed, room=room.name, participant_id=1)

    assert result["result"]["error"] == "invalid_action"
    assert room.players[1].hp == 80
    assert room.players[1].location == "crypt"
    assert room.enemies["goblin"].hp == 12
    assert room.player_histories[1] == [{"action": "inspect", "result": {"damage": 999}}]
    assert room.current_player_id == 1
