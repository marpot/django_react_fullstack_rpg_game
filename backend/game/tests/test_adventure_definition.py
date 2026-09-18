import pytest
from django.contrib.auth import get_user_model

from game.domain.adventure_definition import (
    build_adventure_definition,
    build_cienie_eldorii_definition,
)
from game.state.game_state_manager import GameStateManager
from world.models import Adventure, Choice, Enemy, Location


@pytest.fixture
def cienie_adventure(db):
    user = get_user_model().objects.create_user(username="definition-user")
    adventure = Adventure.objects.create(
        title="Cienie Eldorii", description="Reference slice", creator=user
    )
    village = Location.objects.create(
        adventure=adventure, title="Village", description="Village", order=1
    )
    forest = Location.objects.create(
        adventure=adventure, title="Forest", description="Forest", order=2
    )
    Choice.objects.create(
        location=village, next_location=forest, title="Forest", description=""
    )
    Choice.objects.create(
        location=forest, next_location=village, title="Village", description=""
    )
    Enemy.objects.create(adventure=adventure, name="goblin", hp=20, defense=2)
    return adventure, village, forest


@pytest.mark.django_db
def test_cienie_definition_describes_reference_slice(cienie_adventure):
    adventure, village, forest = cienie_adventure

    definition = build_cienie_eldorii_definition(adventure)

    assert definition.start_location_id == village.id
    assert {npc.id: npc.location_id for npc in definition.npcs} == {
        "guard": village.id,
        "merchant": forest.id,
    }
    assert definition.enemies[0].location_id == forest.id
    assert [step.trigger for step in definition.progression.steps] == [
        "talk:guard@village",
        "defeat:enemy@forest",
        "talk:merchant@forest",
        "move:village",
    ]


@pytest.mark.django_db
def test_definition_does_not_mutate_runtime_room_state(cienie_adventure):
    adventure, _, _ = cienie_adventure
    state = GameStateManager()
    room = state.get_or_create_room("definition-room")
    room.quest.flags["example"] = True
    room.adventure_completed = False
    before = (room.quest.status, dict(room.quest.flags), room.adventure_completed)

    build_cienie_eldorii_definition(adventure)

    assert (room.quest.status, room.quest.flags, room.adventure_completed) == before


@pytest.mark.django_db
def test_generic_builder_does_not_add_reference_progression(db):
    user = get_user_model().objects.create_user(username="generic-definition-user")
    adventure = Adventure.objects.create(
        title="A Generated Adventure", description="Generic slice", creator=user
    )
    Location.objects.create(
        adventure=adventure, title="Harbor", description="Harbor", order=1
    )

    definition = build_adventure_definition(adventure)

    assert definition.progression.steps == ()
    assert all(enemy.location_id is None for enemy in definition.enemies)
    assert all(npc.location_id is None for npc in definition.npcs)
