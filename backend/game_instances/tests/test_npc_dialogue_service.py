import json

import pytest

from game.core.action_processor import ActionProcessor
from game.core.game_command import GameCommand
from game.npc.npc_models import NPC
from game.state.game_state_manager import GameStateManager
from game.state.runtime.models import Player
from game_instances.services.llm.core.llm_client import LLMClient
from game_instances.services.llm.dialogue.npc_dialogue_context import NPCDialogueContextBuilder
from game_instances.services.llm.dialogue.npc_dialogue_service import NPCDialogueService
from game_instances.services.llm.orchestrator.ai_game_master import AIGameMaster


class FakeProvider:
    def __init__(self, answer=None, error=None):
        self.answer = answer
        self.error = error
        self.calls = []

    def complete(self, system_prompt, user_prompt):
        self.calls.append((system_prompt, user_prompt))
        if self.error:
            raise self.error
        return self.answer


def test_dialogue_context_is_bounded_and_serializable():
    runtime_object = object()
    context = NPCDialogueContextBuilder().build(
        {"npc_id": "guide", "npc": "Guide", "personality": "wise",
         "hp": 999, "runtime_npc": runtime_object},
        {"title": "Crypt", "description": "D" * 300,
         "rules": runtime_object, "lore": {"situation": "Dark"}},
        {"actor": "Hero", "location": "crypt", "player_message": "Witaj",
         "recent_actions": ["inspect"] * 8, "room_state": runtime_object},
    )

    json.dumps(context)
    assert context["npc_name"] == "Guide"
    assert context["npc_personality"] == "wise"
    assert context["actor"] == "Hero"
    assert context["world"] == {
        "title": "Crypt", "description": "D" * 160, "situation": "Dark",
    }
    assert context["recent_actions"] == ["inspect"] * 3
    assert "runtime" not in repr(context)
    assert "999" not in repr(context)


def test_dialogue_service_receives_only_canonical_context():
    provider = FakeProvider("Strzeż się cienia w krypcie.")
    service = NPCDialogueService(client=LLMClient(provider))
    context = NPCDialogueContextBuilder().build(
        {"npc_id": "guide", "npc": "Guide", "personality": "wise"},
        {"title": "Crypt"},
        {"actor": "Hero", "location": "crypt", "player_message": "Witaj"},
    )

    assert service.generate(context) == "Strzeż się cienia w krypcie."
    assert len(provider.calls) == 1
    system, user = provider.calls[0]
    assert "STYLE INSTRUCTIONS" in system
    assert "CANONICAL FACTS" in user
    assert json.loads(user.split("\n", 1)[1]) == context


@pytest.mark.parametrize("answer,error", [
    (None, RuntimeError("timeout")),
    (None, None),
    ("{}", None),
    ('{"text":"Witaj"}', None),
])
def test_dialogue_failure_uses_named_fallback(answer, error):
    provider = FakeProvider(answer=answer, error=error)
    context = {"npc_name": "Guide"}

    assert NPCDialogueService(client=LLMClient(provider)).generate(context) == (
        "Guide spogląda na ciebie uważnie, ale nie odpowiada."
    )


@pytest.mark.parametrize("message,npc_id,npc_name", [
    ("talk guide", "guide", "Guide"),
    ("Porozmawiaj ze strażnikiem", "strażnik", "Strażnik"),
])
def test_free_text_talk_uses_same_canonical_processor_path_without_intent_provider(
    message, npc_id, npc_name,
):
    state = GameStateManager()
    room = state.get_or_create_room("dialogue-room")
    room.players[1] = Player(
        id=1, name="Hero", hp=80, max_hp=100, attack_bonus=1,
        damage_die=6, damage_bonus=0, defense=10,
    )
    room.npcs[npc_id] = NPC(id=npc_id, name=npc_name, personality="wise")
    room.turn_order = [1]
    room.current_player_id = 1
    room.player_histories = {1: []}
    provider = FakeProvider(error=AssertionError("intent provider must not run"))
    master = AIGameMaster(intent_client=LLMClient(provider), dialogue_service=NPCDialogueService(
        client=LLMClient(FakeProvider("Witaj, wędrowcze.")),
    ))

    parsed = master.interpret_player_input(
        message, state_manager=state, room=room.name, participant_id=1,
    )
    result = ActionProcessor(state, dialogue_fn=master.dialogue_with_npc).process(
        GameCommand.from_mapping(parsed), room=room.name, participant_id=1,
        player_message=message,
    )

    assert result["action"] == "talk"
    assert result["text"] == "Witaj, wędrowcze."
    assert provider.calls == []
    assert room.players[1].hp == 80
    assert room.current_player_id == 1
    assert room.player_histories == {1: []}
