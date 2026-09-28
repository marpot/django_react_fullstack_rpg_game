from types import SimpleNamespace
from unittest.mock import Mock, patch

from game.domain.adventure_definition import ProgressionDefinition, ProgressionStep
from game.services.adventure_progression_service import AdventureProgressionService


def _room(*, adventure_id=42):
    player = SimpleNamespace(location="village")
    quest = SimpleNamespace(
        status="not_started",
        stage=None,
        objective=None,
        flags={},
        completed=False,
    )
    return SimpleNamespace(
        adventure_id=adventure_id,
        adventure_completed=False,
        players={7: player},
        quest=quest,
    ), player


def _definition(*steps):
    return SimpleNamespace(
        locations=(
            SimpleNamespace(id="village", title="Village"),
            SimpleNamespace(id="forest", title="Forest"),
        ),
        progression=ProgressionDefinition(steps=steps),
    )


def _service(room, player):
    state = Mock()
    state.get_location.return_value = SimpleNamespace(id=player.location)
    return AdventureProgressionService(state), state


def test_advance_without_adventure_is_noop():
    room, player = _room(adventure_id=None)
    service, state = _service(room, player)

    service.advance(room, 7, "talk", {"_npc_id": "guard"})

    state.get_location.assert_not_called()
    assert room.quest.status == "not_started"


def test_first_talk_trigger_starts_quest_and_sets_flag():
    room, player = _room()
    service, _ = _service(room, player)
    definition = _definition(
        ProgressionStep("forest", "talk:guard@Village", "Go to forest", "completed")
    )

    with patch(
        "game.services.adventure_progression_service.build_definition_for_adventure",
        return_value=definition,
    ):
        service.advance(room, 7, "talk", {"_npc_id": "guard"})

    assert room.quest.status == "active"
    assert room.quest.stage == "forest"
    assert room.quest.objective == "Go to forest"
    assert room.quest.flags == {"guard_spoken": True}
    assert room.adventure_completed is False


def test_non_matching_trigger_does_not_change_quest():
    room, player = _room()
    service, _ = _service(room, player)
    definition = _definition(
        ProgressionStep("forest", "talk:guard@Village", "Go to forest", "completed")
    )

    with patch(
        "game.services.adventure_progression_service.build_definition_for_adventure",
        return_value=definition,
    ):
        service.advance(room, 7, "move", {})

    assert room.quest.status == "not_started"
    assert room.quest.stage is None
    assert room.quest.flags == {}


def test_terminal_move_completes_quest_and_adventure():
    room, player = _room()
    room.quest.status = "active"
    room.quest.stage = "forest"
    player.location = "village"
    service, _ = _service(room, player)
    definition = _definition(
        ProgressionStep("forest", "talk:guard@Village", "Go to forest", "completed"),
        ProgressionStep("completed", "move:Village", "", None),
    )

    with patch(
        "game.services.adventure_progression_service.build_definition_for_adventure",
        return_value=definition,
    ):
        service.advance(room, 7, "move", {})

    assert room.quest.status == "completed"
    assert room.quest.stage == "completed"
    assert room.quest.objective is None
    assert room.quest.completed is True
    assert room.adventure_completed is True
