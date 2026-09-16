import pytest
import json

from game_instances.services.llm.narration_service.narration_service import NarrationService
from game_instances.services.llm.narration_service.narration_context import NarrationContextBuilder

pytestmark = pytest.mark.django_db


@pytest.fixture
def service():
    return NarrationService()


def test_intro_fallback(service):
    result = service.intro({
        "adventure": {"title": "Test World"}
    })

    assert "Test World" in result


def test_event_fallback_without_llm(service, monkeypatch):
    monkeypatch.setattr(
        service.client,
        "generate",
        lambda system_prompt, user_prompt: None
    )

    result = service.event({
        "event_type": "combat",
        "result": {"damage": 5},
        "world": {}
    })

    assert "combat" in result


def test_event_calls_llm(service, monkeypatch):
    called = {"flag": False}

    def fake_generate(system_prompt, user_prompt):
        called["flag"] = True
        return "LLM OUTPUT"

    monkeypatch.setattr(service.client, "generate", fake_generate)

    result = service.event({
        "event_type": "combat",
        "result": {"damage": 10},
        "world": {}
    })

    assert called["flag"] is True
    assert result == "LLM OUTPUT"


def test_event_falls_back_when_provider_raises(service, monkeypatch):
    def fail(system_prompt, user_prompt):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(service.client, "generate", fail)

    result = service.event({"event_type": "attack", "result": {"damage": 5}})

    assert result == "Wykonano akcję: attack."


def test_narration_context_only_contains_bounded_plain_facts():
    runtime_object = object()
    context = NarrationContextBuilder().build(
        "attack",
        {"attacker_damage": 7, "defender_damage": 2, "winner": None,
         "runtime": runtime_object, "hp": 999},
        {"title": "Crypt", "description": "Dark" * 100,
         "players": runtime_object, "rules": {"damage": 999}},
        {"actor": "Hero", "target": "goblin", "location": "crypt",
         "room_state": runtime_object, "recent_actions": ["inspect"] * 10},
    )

    json.dumps(context)
    assert context["result"] == {"attacker_damage": 7, "defender_damage": 2}
    assert context["world"] == {"title": "Crypt", "description": "Dark" * 30}
    assert context["recent_actions"] == ["inspect"] * 3
    assert "runtime" not in repr(context)
    assert "999" not in repr(context)


def test_event_prompt_separates_facts_from_style(service, monkeypatch):
    prompts = []
    monkeypatch.setattr(
        service.client, "generate",
        lambda system, user: prompts.append((system, user)) or "Krótka narracja.",
    )

    service.event(NarrationContextBuilder().build(
        "attack", {"attacker_damage": 7, "defender_damage": 0},
    ))

    system, user = prompts[0]
    assert "STYLE INSTRUCTIONS" in system
    assert "CANONICAL FACTS" in user
    assert '"attacker_damage": 7' in user
    assert "dead=true" in system


@pytest.mark.parametrize("output", [
    "Goblin ginie.",
    "Zadajesz 999 obrażeń.",
    '{"text": "Atak udany"}',
])
def test_unconfirmed_death_or_damage_uses_canonical_fallback(service, monkeypatch, output):
    monkeypatch.setattr(service.client, "generate", lambda system, user: output)

    result = service.event({
        "event_type": "attack",
        "result": {"attacker_damage": 7, "defender_damage": 2},
    })

    assert result == "Atak zadaje 7 obrażeń przeciwnikowi. Otrzymujesz 2 obrażeń."
