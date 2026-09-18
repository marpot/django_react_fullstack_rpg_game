from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from game.domain.generated_adventure import (
    GeneratedAdventureSpec,
    GeneratedAdventureValidationError,
    GeneratedChoiceSpec,
    GeneratedEnemySpec,
    GeneratedLocationSpec,
)
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
        npcs=(),
        progression=(),
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
