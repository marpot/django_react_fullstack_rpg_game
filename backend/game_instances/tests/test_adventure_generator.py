import json
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from game.domain.generated_adventure import GeneratedAdventureValidationError

from game_instances.services.llm.adventure_generator import (
    GeneratedAdventureGenerationError,
    GeneratedAdventureGenerator,
)
from world.models import Adventure


def valid_payload():
    return {
        "title": "The Generated Crossing",
        "description": "A generated test adventure.",
        "start_location": "village",
        "locations": [
            {"key": "village", "title": "Village", "description": "Home."},
            {"key": "forest", "title": "Forest", "description": "Trees."},
        ],
        "choices": [
            {
                "title": "Enter forest",
                "description": "Take the path.",
                "from_location": "village",
                "to_location": "forest",
            },
        ],
        "enemies": [
            {
                "key": "wolf",
                "name": "Wolf",
                "location": "forest",
                "hp": 18,
                "defense": 4,
                "attack_bonus": 3,
                "damage_die": 6,
                "damage_bonus": 1,
            },
        ],
        "npcs": [],
        "progression": [
            {
                "stage": "forest",
                "trigger": "move:Forest",
                "objective": "Defeat the wolf.",
                "next_stage": "completed",
            },
            {
                "stage": "completed",
                "trigger": "defeat:enemy@Forest",
                "objective": "",
                "next_stage": None,
            },
        ],
    }


def test_valid_json_becomes_generated_adventure_spec():
    client = Mock()
    client.generate.return_value = json.dumps(valid_payload())

    spec = GeneratedAdventureGenerator(client).generate("Build an adventure")

    assert spec.title == "The Generated Crossing"
    assert spec.locations[0].key == "village"
    assert spec.enemies[0].hp == 18
    client.generate.assert_called_once()


def test_malformed_json_is_a_controlled_failure():
    client = Mock()
    client.generate.return_value = "not json"

    with pytest.raises(GeneratedAdventureGenerationError):
        GeneratedAdventureGenerator(client).generate("Build an adventure")


def test_invalid_references_fail_validation():
    payload = valid_payload()
    payload["start_location"] = "unknown"
    client = Mock()
    client.generate.return_value = json.dumps(payload)

    with pytest.raises(GeneratedAdventureValidationError):
        GeneratedAdventureGenerator(client).generate("Build an adventure")


@pytest.mark.django_db
def test_endpoint_persists_valid_llm_output():
    user = get_user_model().objects.create_user(username="generator-user")
    client = APIClient()
    client.force_authenticate(user=user)
    llm_client = Mock()
    llm_client.generate.return_value = json.dumps(valid_payload())

    with patch(
        "game_instances.services.llm.adventure_generator.LLMClient",
        return_value=llm_client,
    ):
        response = client.post(
            "/api/world/adventures/generate/",
            {"prompt": "Build an adventure"},
            format="json",
        )

    assert response.status_code == 200
    assert Adventure.objects.filter(title="The Generated Crossing").exists()


@pytest.mark.django_db
@pytest.mark.parametrize("failure", [RuntimeError("provider down"), "not json"])
def test_endpoint_uses_procedural_fallback_on_generation_failure(failure):
    user = get_user_model().objects.create_user(username="fallback-user")
    client = APIClient()
    client.force_authenticate(user=user)

    provider_client = Mock()
    if isinstance(failure, Exception):
        provider_client.generate.side_effect = failure
    else:
        provider_client.generate.return_value = failure

    with patch(
        "game_instances.services.llm.adventure_generator.LLMClient",
        return_value=provider_client,
    ), patch(
        "world.factories.adventure_factory.random.choice",
        side_effect=lambda values: values[0],
    ):
        response = client.post(
            "/api/world/adventures/generate/",
            {"prompt": "Build an adventure"},
            format="json",
        )

    assert response.status_code == 200
    assert Adventure.objects.filter(creator=user).count() == 1


@pytest.mark.django_db
def test_building_definition_does_not_call_llm_again():
    user = get_user_model().objects.create_user(username="definition-user")
    llm_client = Mock()
    llm_client.generate.return_value = json.dumps(valid_payload())

    with patch(
        "game_instances.services.llm.adventure_generator.LLMClient",
        return_value=llm_client,
    ):
        spec = GeneratedAdventureGenerator().generate("Build an adventure")
        from world.factories.adventure_factory import AdventureFactory
        from game.domain.adventure_definition import build_adventure_definition

        adventure = AdventureFactory.create_from_spec(user, spec)
        build_adventure_definition(adventure)

    assert llm_client.generate.call_count == 1
