import json

from game_instances.services.llm.core.llm_client import LLMClient


class FakeProvider:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def complete(self, system_prompt, user_prompt):
        self.calls.append((system_prompt, user_prompt))
        return self.response


def parse_json(text: str):
    text = text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        text = text.replace("json", "").strip()

    return json.loads(text)


def test_llm_returns_valid_intent_json():
    provider = FakeProvider('{"action":"attack","target":"goblin","method":"spell"}')
    llm_client = LLMClient(provider)

    player_input = "attack goblin with spell"
    response_text = llm_client.generate_intent(
        "SYSTEM: return JSON only",
        player_input
    )

    intent = parse_json(response_text)

    assert "action" in intent
    assert "target" in intent
    assert "method" in intent
    assert "STRICT JSON intent parser" in provider.calls[0][0]
    assert provider.calls[0][1] == player_input


def test_llm_maps_inputs_to_allowed_actions():
    provider = FakeProvider('{"action":"move","target":"north","method":null}')
    llm_client = LLMClient(provider)

    allowed_actions = {
        "attack",
        "move",
        "inspect",
        "talk",
        "defend",
        "use_item",
    }

    response_text = llm_client.generate_intent(
        "SYSTEM: return JSON only",
        "go north"
    )

    intent = parse_json(response_text)

    assert isinstance(intent["action"], str)
    assert intent["action"] in allowed_actions

    assert isinstance(intent.get("target"), (str, type(None)))
    assert isinstance(intent.get("method"), (str, type(None)))


def test_llm_does_not_return_game_state():
    llm_client = LLMClient(FakeProvider(
        '{"action":"attack","target":"goblin","method":null,'
        '"hp":1,"damage":99,"result":"win","message":"changed"}'
    ))

    response_text = llm_client.generate_intent(
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


def test_plain_generation_preserves_narration_text():
    provider = FakeProvider("Bohater trafia goblina.")
    client = LLMClient(provider)

    assert client.generate("Opowiedz wynik.", "Trafienie za 5 obrażeń") == provider.response
    assert provider.calls == [("Opowiedz wynik.", "Trafienie za 5 obrażeń")]
