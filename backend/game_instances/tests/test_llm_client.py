import json
import pytest
from game_instances.services.llm.core.llm_client import LLMClient

pytestmark = pytest.mark.django_db


def parse_json(text: str):
    text = text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        text = text.replace("json", "").strip()

    return json.loads(text)


def test_llm_returns_valid_intent_json():
    llm_client = LLMClient()

    player_input = "attack goblin with spell"
    response_text = llm_client.generate(
        "SYSTEM: return JSON only",
        player_input
    )

    intent = parse_json(response_text)

    assert "action" in intent
    assert "target" in intent
    assert "method" in intent


def test_llm_maps_inputs_to_allowed_actions():
    llm_client = LLMClient()

    test_inputs = [
        "attack goblin",
        "go north",
        "look around",
        "attack goblin with spell",
    ]

    allowed_actions = {
        "attack",
        "move",
        "inspect",
        "talk",
        "defend",
        "use_item",
    }

    for player_input in test_inputs:
        response_text = llm_client.generate(
            "SYSTEM: return JSON only",
            player_input
        )

        intent = parse_json(response_text)

        assert isinstance(intent["action"], str)
        assert intent["action"] in allowed_actions

        assert isinstance(intent.get("target"), (str, type(None)))
        assert isinstance(intent.get("method"), (str, type(None)))


def test_llm_does_not_return_game_state():
    llm_client = LLMClient()

    response_text = llm_client.generate(
        "SYSTEM: return JSON only",
        "attack goblin"
    )

    intent = parse_json(response_text)

    forbidden_fields = [
        "hp",
        "health",
        "damage",
        "result",
        "message",
    ]

    for field in forbidden_fields:
        assert field not in intent