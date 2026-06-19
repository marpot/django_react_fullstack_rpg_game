import pytest
from unittest.mock import MagicMock

from game_instances.services.llm.narration_service import NarrationService


@pytest.fixture
def service():
    return NarrationService()


def test_intro_fallback(service):
    result = service.intro({
        "adventure": {"title": "Test World"}
    })

    assert "Test World" in result


def test_event_fallback_without_llm(service, monkeypatch):
    # mock LLMClient.generate
    monkeypatch.setattr(
        service.client,
        "generate",
        lambda prompt: None
    )

    result = service.event({
        "event_type": "combat",
        "result": {"damage": 5},
        "world": {}
    })

    assert "combat" in result
    assert "damage" in result

def test_event_calls_llm(service, monkeypatch):
    called = {"flag": False}

    def fake_generate(prompt):
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