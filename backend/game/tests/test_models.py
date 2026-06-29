import pytest
from accounts.models import PlayerCharacter
from game.models import GameEvent, GameSession


@pytest.fixture
def test_player_character(db, test_user, test_adventure, test_location):
    return PlayerCharacter.objects.create(
        user=test_user,
        name="Testowa_postac",
        current_location=test_location,
        adventure=test_adventure,
        stats={"strength": 10, "agility": 8}
    )


@pytest.fixture
def test_game_event(db, test_player_character, test_adventure):
    return GameEvent.objects.create(
        player=test_player_character,
        location=None,
        description="Test description",
        adventure=test_adventure,
        event_type=GameEvent.EventType.STORY
    )


@pytest.fixture
def test_game_session(db, test_player_character, test_adventure):
    return GameSession.objects.create(
        player=test_player_character,
        adventure=test_adventure,
        progress={"level": 1},
    )


def test_game_session_creation(test_game_session):
    assert test_game_session.created_at is not None
    assert test_game_session.updated_at is not None
    assert test_game_session.created_at <= test_game_session.updated_at


def test_game_event_creation(test_game_event):
    event = GameEvent.objects.get(id=test_game_event.id)

    assert GameEvent.objects.count() == 1
    assert event.player == test_game_event.player
    assert event.description == "Test description"
    assert event.adventure == test_game_event.adventure