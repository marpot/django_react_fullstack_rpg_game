from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from game.domain.generated_adventure import (
    GeneratedAdventureSpec,
    GeneratedAdventureValidationError,
    GeneratedChoiceSpec,
    GeneratedEnemySpec,
    GeneratedLocationSpec,
    GeneratedNPCSpec,
    GeneratedProgressionStep,
)
from game.domain.adventure_definition import build_definition_for_adventure
from world.factories.adventure_factory import AdventureFactory
from world.models import Adventure, Choice, Enemy, Location


def build_spec() -> GeneratedAdventureSpec:
    return GeneratedAdventureSpec(
        title="Generated test adventure",
        description="Persisted from a generated spec.",
        start_location="village",
        locations=(
            GeneratedLocationSpec("village", "Village", "A quiet village."),
            GeneratedLocationSpec("forest", "Forest", "A dark forest."),
        ),
        choices=(
            GeneratedChoiceSpec(
                "Enter forest", "Follow the path.", "village", "forest"
            ),
        ),
        enemies=(
            GeneratedEnemySpec(
                "goblin", "Goblin", "forest", 20, 3, 4, 8, 2
            ),
        ),
        npcs=(
            GeneratedNPCSpec("guard", "Guard", "vigilant", "village"),
        ),
        progression=(
            GeneratedProgressionStep(
                "forest", "talk:guard@Village", "Enter the forest.", "completed"
            ),
            GeneratedProgressionStep(
                "completed", "defeat:enemy@Forest", "", None
            ),
        ),
    )


@pytest.fixture
def creator(db):
    return get_user_model().objects.create_user(username="factory-user")


@pytest.mark.django_db
def test_create_from_spec_persists_world_records(creator):
    adventure = AdventureFactory.create_from_spec(creator, build_spec())

    assert Adventure.objects.filter(pk=adventure.pk).count() == 1
    assert adventure.locations.count() == 2
    assert adventure.enemies.count() == 1
    assert Choice.objects.filter(location__adventure=adventure).count() == 1

    choice = Choice.objects.get(location__adventure=adventure)
    assert choice.location.title == "Village"
    assert choice.next_location.title == "Forest"
    assert choice.title == "Enter forest"
    assert choice.description == "Follow the path."

    enemy = adventure.enemies.get()
    assert (
        enemy.name,
        enemy.hp,
        enemy.defense,
        enemy.attack_bonus,
        enemy.damage_die,
        enemy.damage_bonus,
    ) == ("Goblin", 20, 3, 4, 8, 2)


@pytest.mark.django_db
def test_generated_scenario_round_trips_into_adventure_definition(creator):
    spec = build_spec()
    adventure = AdventureFactory.create_from_spec(creator, spec)

    definition = build_definition_for_adventure(adventure)
    location_ids = {
        location.title: location.id for location in definition.locations
    }

    assert [
        (step.stage, step.trigger, step.objective, step.next_stage)
        for step in definition.progression.steps
    ] == [
        (step.stage, step.trigger, step.objective, step.next_stage)
        for step in spec.progression
    ]
    assert definition.enemies[0].location_id == location_ids["Forest"]
    assert definition.npcs[0].id == "guard"
    assert definition.npcs[0].personality == "vigilant"
    assert definition.npcs[0].location_id == location_ids["Village"]


@pytest.mark.django_db
def test_invalid_spec_does_not_create_adventure(creator):
    spec = build_spec()
    invalid = GeneratedAdventureSpec(**{**spec.__dict__, "start_location": "unknown"})

    with pytest.raises(GeneratedAdventureValidationError):
        AdventureFactory.create_from_spec(creator, invalid)

    assert Adventure.objects.count() == 0


@pytest.mark.django_db
def test_create_from_spec_rolls_back_on_persistence_error(creator):
    with patch(
        "world.factories.adventure_factory.Enemy.objects.create",
        side_effect=RuntimeError("enemy write failed"),
    ):
        with pytest.raises(RuntimeError, match="enemy write failed"):
            AdventureFactory.create_from_spec(creator, build_spec())

    assert Adventure.objects.count() == 0
    assert Location.objects.count() == 0
    assert Choice.objects.count() == 0
    assert Enemy.objects.count() == 0
